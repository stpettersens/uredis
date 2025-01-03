#
# μRedis Server: a minimal clone of Redis server
# Copyright 2024 Sam Saint-Pettersen
#
# Released under the MIT License.
#
# $server

import os
import re
import sys
import signal
import getopt
import socket
import pickle
import logging
import selectors

from uuid import UUID
from time import sleep
from typing import TypeAlias
from datetime import datetime
from threading import Thread, Event

from server_pkg.logs import Logs
from tokenizer.resp_token import TokenKind
from parser.resp_parser import Parser
from server_pkg.exit_params import ExitParams
from server_pkg.connections import Connections
from redis.redis_records import RedisRecords
from parser.execute_command import execute_command
from colors.print_colors import print_green, print_gray
from detection.detection import is_windows, get_platform, get_arch

Socket: TypeAlias = socket.socket
sel = selectors.DefaultSelector()

def validate_ip_v4(ip: str) -> bool:
    if ip.strip() == '0.0.0.0': # Bind all is allowable.
        return True

    results = re.findall(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$', ip)
    if not results:
        return False

    matches = list(results[0])
    for m in matches:
        if int(m) > 255:
            return False

    return True

def get_version() -> str:
    version: str = '0.2.0'
    return version

def display_version() -> int:
    print('uRedis Server {} on {} ({})'.format(get_version(), get_platform(), get_arch()))
    return 0

def display_logo(colors: bool) -> None:
    logo: str = r"""
       ____  _____ ____ ___ ____
 _   _|  _ \| ____|  _ \_ _/ ___|
| | | | |_) |  _| | | | | |\___ \
| |_| |  _ <| |___| |_| | | ___) |
 \__,_|_| \_\_____|____/___|____/

                           SERVER
 """
    if colors:
        print("\033[31m{}\033[0m".format(logo));
    else:
        print(logo)

def save_records(working_dir: str, records: RedisRecords, dump_db: str, max_size: int) -> None:
    path_db: str = os.path.join(working_dir, dump_db)
    if max_size != -1 and os.path.exists(path_db) and os.path.getsize(path_db) >= max_size:
        os.remove(path_db)

    if records.get_number() == 0:
        if os.path.exists(path_db):
            os.remove(path_db)
            print('Cleared {} (0 records).'.format(dump_db))
        return

    print('Saving {} record(s) to {}...'
    .format(records.get_number(), dump_db))
    with open(path_db, 'wb') as urdb:
        pickle.dump(records, urdb)

def load_records(working_dir: str, dump_db: str) -> RedisRecords|None:
    path_db: str = os.path.join(working_dir, dump_db)
    records = None
    if os.path.exists(path_db):
        with open(path_db, 'rb') as urdb:
            records = pickle.load(urdb)
            print('Loaded {} record(s) from {}.'
            .format(records.get_number(), dump_db))

    return records

def decay_ttl_records(records: RedisRecords, stop_event: Event) -> None:
    print('Started TTL record(s) decay thread.')
    while not stop_event.is_set():
        sleep(1)
        for k in records.get_keys():
            r = records.get_record(k)
            if r.get_ttl() == -1:
                continue
            if r.get_ttl() == 0:
                records.delete_record(k)
            else:
                r.decrement_ttl()

    print('Stop decaying TTL record(s)...')

def save_records_on_change(working_dir: str, records: RedisRecords, dump_db: str, max_size: int, stop_event: Event) -> None:
    _uuid: UUID = records.get_uuid()
    print('Started record(s) changes thread.')
    while not stop_event.is_set():
        if records.has_changed(_uuid):
            save_records(working_dir, records, dump_db, max_size)
            _uuid = records.get_uuid()

    print('Stop record(s) changes thread...')

def daemon_write_pid(daemon_dir: str) -> None:
    with open(os.path.join(daemon_dir, 'uredis.pid'), 'w') as pid:
        pid.write(str(os.getpid()))

def display_header(colors: bool = False) -> None:
    display_logo(colors)
    print('uRedis Server: a minimal clone of Redis server ({} {}, {})'
    .format(get_version(), get_platform(), get_arch()))
    print('Copyright 2024-2025 Sam Saint-Pettersen <s.stpettersen@pm.me>.')
    print()

def display_error(message: str) -> int:
    print("Error: {}.".format(message))
    print()
    return display_usage(-1)

def display_usage(exit_code: int) -> int:
    display_header()
    print('CLI options are:')
    print()
    print('-h | --help: Display this usage information and exit.')
    print('-v | --version: Display version information and exit.')
    print()
    print('-b <ip>: Set the host IP address to bind to (e.g. 127.0.0.1/0.0.0.0).')
    print('-p | --port <port>: Set port to use for server (default = 6379 as redis-server).')
    print('-x | --protocol <2|3>: Set Redis protocol version as 2 or 3 (default = 2).')
    print('-d | --db <db_name>: Set file name for URDB (μRDB file; default = dump.urdb).')
    print('-l | --log <log_file>: Set file name for log file (default = uredis.log).')
    print('-n | --no-log: Disable logging client operations.')
    print('-u | --update-disk: Write changes to disk every time records are added or removed.')
    print('-m | --no-disk: Do not load from or write any changes to disk (only keep records in memory).')
    print('-c | --colorless: Do not use colors in console.')
    print('-r | --dir: Set working directory for the server incl. trailing slash (e.g. /opt/uredis/).')
    print('-z | --max-db: Set max size for disk file in bytes.')
    print()
    print('-s | --daemon-safe: Run in daemon safe mode (writing changes behaves the same as --update-disk')
    print('\t  unless --no-disk). Daemon safe mode is always colorless.')
    print()
    print('-i | --no-pid: Do not write a uredis.pid file containing server process process id (pid).')
    print()
    print('Note: uredis.pid file is only written when running in daemon safe mode')
    print('w/o the --no-pid switch. The --no-pid switch as no effect outside of daemon safe mode.')
    print()
    return exit_code

def print_log(message: str, logs: Logs, log_only: bool = False) -> None:
    if not log_only:
        print(message)

    if logs == Logs.LOGGING:
        logging.info(message)

def term_log(log_file: str) -> None:
    if os.path.exists(log_file) and os.path.getsize(log_file) >= 100_000_000:
        os.remove(log_file)
        logging.info('[TRUNCATED]')

def accept(s: Socket, logs: Logs, records: RedisRecords, protocol: int, port: int) -> None:
      conn, addr = s.accept()
      Connections().set(conn.getpeername())
      cid: int = Connections().get(conn.getpeername())
      print('Connected to client {} (#{})'.format(addr, cid))
      conn.setblocking(True)
      sel.register(conn, selectors.EVENT_READ, read)

def read(conn: Socket, logs: Logs, records: RedisRecords, protocol: int, port: int) -> None:
      cid: int = Connections().get(conn.getpeername())
      data: bytes = conn.recv(1024)
      params: bytes = b''

      if data.find(b'\r\n') != -1:
          # RESP Messages:
          if data.startswith(b'*'):
              resp_str: str = data.decode('utf-8')
              parser = Parser(resp_str)
              cmd: bytes = b''
              params_list: list[bytes] = []
              for token in parser.get_tokens():
                  if token.kind() == TokenKind.CMD:
                      cmd = str.encode(token.value())

                  elif token.kind() == TokenKind.PARAM:
                      params_list.append(str.encode(token.value()))

              pams: bytes = b' '.join(params_list)
              execute_command(conn, port, cid, logs, get_version(), records, protocol, cmd, pams)

          # Raw input from TCP clients:
          elif data.find(b'\r\n') != -1:
              msgs: list[bytes] = data.split(b'\r\n')
              for m in msgs:
                  if m == b'':
                      continue

                  elif m.find(b' ') == -1:
                      command: bytes = m
                      execute_command(conn, port, cid, logs, get_version(), records, protocol, command)

                  else:
                      command, params = tuple(m.split(b' ', 1))
                      execute_command(conn, port, cid, logs, get_version(),
                      records, protocol, command, params)

          else:
              print('Closing connection to client: {}'.format(conn.getpeername()))
              sel.unregister(conn)
              conn.close()

# !!!
def foo(signum, frame) -> None:
    print('Received signal:')
    print(signum)
    sys.exit(0)

def exit_server(ep: ExitParams) -> None:
    ep.stop_event.set() # Stop thread(s)
    sleep(3)
    if not ep.no_disk:
        save_records(ep.working_dir, ep.records, ep.dump_db, ep.max_size) # Save records as-is
    print_log('Terminating...', ep.logs)

    if ep.logs == Logs.LOGGING:
        term_log(ep.log_file)

    sys.exit(0)

def main(args: list[str]) -> None:
    host: str = '127.0.0.1'
    port: int = 6379
    protocol: int = 2
    dump_db: str = 'dump.urdb'
    log_file: str = 'uredis.log'
    logs: Logs = Logs.LOGGING
    update_disk: bool = False
    no_disk: bool = False
    daemon: bool = False
    dump_pid: bool = True
    colors: bool = True
    working_dir = str(sys.path[0]).strip()
    max_size: int = -1

    start_time: datetime = datetime.now()

    if is_windows():
        pass
        #signal.signal(signal.SIGBREAK, foo)
        #signal.raise_signal(signal.SIGBREAK) # !!!

    try:
        opts, args = getopt.getopt(args, "hvb:p:x:d:l:numcr:z:si",
        [
            "help", "version", "bind=", "port=", "protocol=", "db=", "log=", "no-log", "update-disk",
            "no-disk", "colorless", "dir=", "max-db=", "daemon-safe", "no-pid"
        ])

    except getopt.GetoptError as e:
        sys.exit(display_error(str(e)))

    for o, a in opts:
        if o in ("-h", "--help"):
            sys.exit(display_usage(0))

        if o in ("-v", "--version"):
            sys.exit(display_version())

        if o in ("-b", "--bind"):
            try:
                if not validate_ip_v4(a):
                    raise ValueError

                host = a

            except ValueError:
                sys.exit(display_error('Host (-b/--bind) must be a valid v4 IP address'))

        if o in ("-p", "--port"):
            try:
                port = int(a)
                if port <= 0:
                    raise ValueError

            except ValueError:
                sys.exit(display_error('Port must be a positive integer such as 6379'))

        if o in ("-x", "--protocol"):
            try:
                protocol = int(a)
                if protocol < 2 or protocol > 3:
                    raise ValueError

            except ValueError:
                sys.exit(display_error('Protocol must be either 2 or 3'))

        if o in ("-d", "--db"):
            dump_db = a

        if o in ("-l", "--log"):
            log_file = a

        if o in ("-n", "--no-log"):
            logs = Logs.NO_LOGGING

        if o in ("-u", "--update-disk"):
            update_disk = True

        if o in ("-m", "--no-disk"):
            no_disk = True

        if o in ("-c", "--colorless"):
            colors = False

        if o in ("-r", "--dir"):
            working_dir = a

        if o in ("-z", "--max-db"):
            try:
                max_size = int(a)
                if max_size < 1000:
                    raise ValueError

            except ValueError:
                sys.exit(display_error('Max DB size must be 1000 (1KB) or more bytes'))

        if o in ("-s", "--daemon-safe"):
            daemon = True

        if o in ("-i", "--no-pid"):
            dump_pid = False

    if daemon:
        colors = False

    if working_dir.find('uredis-server.pyz') != -1:
        working_dir = working_dir.replace("uredis-server.pyz", "")[0:-1]

    if daemon and dump_pid:
        daemon_write_pid(working_dir)

    log_file = os.path.join(working_dir, log_file)
    dump_db = os.path.join(working_dir, dump_db)

    display_header(colors)

    if daemon:
        print('** DAEMON SAFE MODE **')
        if not no_disk:
            print()

    if no_disk:
        print('** MEMORY ONLY MODE **')
        print()

    print_green('[ Host = {}, Port = {}, Protocol = {}, PID = {} ]'.format(host, port, protocol, os.getpid()), colors)
    print_green('[ Working dir = "{}" ]'.format(working_dir), colors)

    max_db = "UNLIMITED" if max_size == -1 else str(max_size) + " bytes"
    if no_disk:
        max_db = "N/A"

    print_green('[ Maximum DB file size = {} ]'.format(max_db), colors)
    print()

    print_gray('Press Ctrl+C to terminate.', colors);
    print()

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='[%(asctime)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    print_log('Started uRedis server ({}) on {}:{} #PID = {}...'
    .format(get_version(), host, port, os.getpid()), logs, log_only=True)

    print_log('Server started at {}.'.format(start_time), logs)

    records: RedisRecords|None = None
    if not no_disk:
        records = load_records(working_dir, dump_db)

    if records == None:
       print('Initializing new records collection.')
       records = RedisRecords()

    stop_event: Event = Event()
    ttl_thread: Thread = Thread(target=decay_ttl_records, args=(records, stop_event))
    ttl_thread.start()

    if (daemon or update_disk) and not no_disk:
        changes_thread: Thread = Thread(target=save_records_on_change,
        args=(working_dir, records, dump_db, max_size, stop_event))
        changes_thread.start()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print('Listening on {}:{}...'.format(host, port))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            s.listen()
            s.setblocking(True)
            sel.register(s, selectors.EVENT_READ, accept)

            while True:
                events: list = sel.select()
                for key, _ in events:
                    callback = key.data
                    callback(key.fileobj, logs, records, protocol, port)

    except OSError as e:
        print_gray('Is another server running on port {}?'.format(port), colors)
        print_gray(str(e), colors)

    except KeyboardInterrupt:
        ep: ExitParams = ExitParams(
            working_dir,
            records,
            stop_event,
            dump_db,
            no_disk,
            max_size,
            logs,
            log_file)
        exit_server(ep)

    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])
