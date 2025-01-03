# $server

import socket
import math
import logging

from typing import TypeAlias
from datetime import datetime

from server_pkg.logs import Logs
from redis.redis_error import RedisError
from redis.redis_hello import RedisHello
from redis.redis_info import RedisInfo
from redis.redis_ping import RedisPing
from redis.redis_echo import RedisEcho
from redis.redis_record import RedisRecord
from redis.redis_records import RedisRecords
from resp.resp_commands import RespCommands

Socket: TypeAlias = socket.socket

def print_log(message: str|bytes, logs: Logs, request: bool = False) -> None:
    if logs == Logs.NO_LOGGING:
        return

    msg: str = ''
    if not request:
        msg = 'Server responded with: '

    msg += str(message)
    logging.info(msg.strip())

def execute_command(conn: Socket, port: int, cid: int, num_conns: int,
working_dir: str, logs: Logs, version: str, records: RedisRecords, protocol: int, start_time: datetime, command: bytes, params: bytes = b'') -> None:
    if params == b'':
        print_log('Client {} sent request: {}'
        .format(conn.getpeername(), command.decode('utf-8')), logs, True)
    else:
        print_log('Client {} sent request: {} with {}'
        .format(conn.getpeername(), command.decode('utf-8'),
        params.decode('utf-8')), logs, True)

    str_command: str = command.decode('utf-8')
    str_params: str = params.decode('utf-8')

    if not str_command in RespCommands().get():
        error = RedisError("unknown '{}' command".format(str_params.lower()))
        print_log(error.get(), logs)
        conn.send(error.get())

    elif command == b'HELLO':
        if len(params) == 0:
            error = RedisError("wrong number of arguments for 'hello' command")
            print_log(error.get(), logs)
            conn.send(error.get())
        else:
            hello = RedisHello(params, cid, version)
            print_log(hello.get(), logs)
            conn.send(hello.get())

    elif command == b'INFO':
        info = RedisInfo(working_dir, version, num_conns, port, start_time)
        if len(params) == 0:
            print_log(info.get(), logs)
            conn.send(info.get())
        else:
            print_log(info.get(params), logs)
            conn.send(info.get(params))

    elif command == b'CLIENT':
        print_log(b'+OK\r\n', logs)
        conn.send(b'+OK\r\n')

    elif command == b'PING':
        pong = RedisPing(params)
        print_log(pong.get(), logs)
        conn.send(pong.get())

    elif command == b'ECHO':
        if len(params) == 0:
            error = RedisError("wrong number of arguments for 'echo' command")
            print_log(error.get(), logs)
            conn.send(error.get())
        else:
            echo = RedisEcho(params)
            print_log(echo.get(), logs)
            conn.send(echo.get())

    elif command == b'SET':
        if len(params) < 2:
            error = RedisError("wrong number of arguments for 'set' command")
            print_log(error.get(), logs)
            conn.send(error.get())
        else:
            p = params.split()
            if len(p) == 2:
                record = RedisRecord(p[1])

                # !!!
                import sys
                print('Record is {} bytes.'.format(sys.getsizeof(record)))
                # !!!

                records.push_record(p[0], record)
                print_log(record.ok(), logs)
                conn.send(record.ok())

            elif len(p) == 4:
                try:
                    ttl: int = abs(math.ceil(int(p[3])))
                    if ttl <= 0:
                        raise ValueError("ttl must be a + integer value in seconds or milliseconds")

                    if p[2].upper() == b'EX': # TTL seconds
                        pass

                    elif p[2].upper() == b'PX': # TTL milliseconds
                        ttl = int((ttl / 1000))

                    else:
                        raise ValueError("ttl must be 'ex' (seconds) or 'px' (milliseconds)")

                    record = RedisRecord(p[1], ttl)
                    records.push_record(p[0], record)
                    print_log(record.ok(), logs)
                    conn.send(record.ok())

                except ValueError as message:
                    error = RedisError(str(message))
                    print_log(error.get(), logs)
                    conn.send(error.get())

    elif command == b'GET':
        if len(params) == 0:
            error = RedisError("wrong number of arguments for 'get' command")
            print_log(error.get(), logs)
            conn.send(error.get())
        else:
            record = records.get_record(params.split()[0])
            if record.is_dummy():
                if protocol == 2:
                    print_log(b'$0\r\n\r\n', logs)
                    conn.send(b'$0\r\n\r\n')

                elif protocol == 3:
                    print_log(b'_\r\n', logs)
                    conn.send(b'_\r\n')
            else:
                print_log(record.get(), logs)
                conn.send(record.get())

    elif command == b'TTL':
        if len(params) == 0:
            error = RedisError("wrong number of arguments for 'ttl' command")
            print_log(error.get(), logs)
            conn.send(error.get())
        else:
            record = records.get_record(params.split()[0])
            if record.is_dummy():
                print_log('b:-2\r\n', logs)
                conn.send(b':-2\r\n')
            else:
                ttl_bytes: bytes = record.get_ttl_as_bytes()
                print_log(ttl_bytes, logs)
                conn.send(ttl_bytes)

    elif command == b'DEL':
        if len(params) == 0:
            error = RedisError("wrong number of arguments for 'del' command")
            print_log(error.get(), logs)
            conn.send(error.get())
        else:
            deleted: bytes = records.delete_record(params.split()[0])
            print_log(deleted, logs)
            conn.send(deleted)

    elif command == b'FLUSHDB' or command == b'FLUSHALL':
        deleted_flush: bytes = records.delete_all_records()
        print_log(deleted_flush, logs)
        conn.send(deleted_flush)

    elif command == b'KEYS':
        if len(params) == 0:
            error = RedisError("wrong number of arguments for 'keys' command")
            print_log(error.get(), logs)
            conn.send(error.get())
        elif params == b'*':
            print_log(records.get_keys_as_bytes(), logs)
            conn.send(records.get_keys_as_bytes())
