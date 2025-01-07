#
# μRedis Client: a minimal clone of Redis CLI
# Copyright 2024 Sam Saint-Pettersen
#
# Released under the MIT License.
#
# $client

import sys
import getopt
import socket
import platform

from typing import TypeAlias

from detection.detection import *
from colors.print_colors import *
from resp.resp_type import RespType
from resp.resp_encoder import RespEncoder
from resp.resp_decoder import RespDecoder

Socket: TypeAlias = socket.socket
g_conn: bytes = b''

def get_version() -> str:
    version: str = '0.2.0'
    return version

def display_version() -> int:
    print('uRedis Client {} on {} ({})'.format(get_version(), get_platform(), get_arch()))
    return 0

def display_header(no_prompt: bool, colors: bool = False) -> None:
    print('μRedis Client: a minimal clone of Redis CLI ({} {}, {})'
    .format(get_version(), get_platform(), get_arch()))
    print('Copyright 2024-2025 Sam Saint-Pettersen <s.stpettersen@pm.me>.')
    print()
    if not no_prompt:
        if is_windows():
            print_cyan('Use a ; in a line to separate commands.', colors)
        else:
            print_cyan('Use a semicolon in a line to separate commands.', colors)

        print_cyan('ATTENTION: Not currently compatible with official Redis server.', colors)
        print()
        print_gray('Exit the client with EXIT, clear the screen with CLEAR/CLS', colors)
        print_gray('and display this help message with HELP.', colors)
        print()

def display_usage(exit_code: int) -> int:
    display_header(no_prompt=True)
    print('CLI options are:')
    print()
    print('-h | --help: Display this usage information and exit.')
    print('-v | --version: Display version information and exit.')
    print()
    print('-r | --resp: Show RESP messages sent to server.')
    print('-c | --colorless: Do not use colors in console.')
    print('-p | --port: Port number for running server.')
    return exit_code

def format_resp(cmd: bytes) -> str:
    return cmd.decode('utf-8').replace('\r', '<CR>').replace('\n', '<LF>')

def get_conn(s: Socket) -> None:
    s.send(b'_GET_CONN\r\n')
    global g_conn
    g_conn = s.recv(1024)
    print(g_conn)

def drop_conn(s: Socket) -> None:
    global g_conn
    s.send((b'_DROP_CONN ' + g_conn))

def exit_client(s: Socket) -> None:
    drop_conn(s)
    s.shutdown(socket.SHUT_RD)
    s.close()
    sys.exit(0)

def execute(command: str, s: Socket, host: str, port: int, colors: bool, show_resp: bool) -> None:
    if command.upper() == 'CLS' or command.upper() == 'CLEAR':
        clear_screen()
        return

    match command.upper():
        case 'EXIT':
            exit_client(s)

        case 'HELP':
            clear_screen()
            display_header(no_prompt=False, colors=colors)
            return

    encoder = RespEncoder(command)
    for cmd in encoder.encode():
        if show_resp:
            if is_unix_like():
                print_yellow(format_resp(cmd), colors)
            else:
                print_yellow_bytes(cmd, colors)

        s.send(cmd)
        response, _type = RespDecoder(s.recv(1024), cmd).decode()

        match _type:
            case RespType.STATUS:
                print_green(response, colors)

            case RespType.ERROR:
                print_red(response, colors)

            case RespType.NUMBER:
                print_magenta(response, colors)

            case RespType.KEYS:
                print_gray(response, colors, pattern=')')

            case RespType.KEYVALS:
                print_gray(response, colors, pattern='=>')

            case RespType.SHOULD_NOT_SEND:
                print_red("The command '{}' should not be sent by users."
                .format(response), colors)

            case RespType.EMPTY:
                # We should never get this response.
                print_red('Response was empty. :(', colors)

            case _:
                print(response)

def main(args: list[str]) -> None:
    host: str = '127.0.0.1'
    port: int = 6379
    show_resp: bool = False
    colors: bool = True

    try:
        opts, args = getopt.getopt(args, "hvrcp:",
        [
            "help", "version", "resp", "colorless", "port:"
        ])

    except getopt.GetoptError as e:
        print('Error: {}'.format(e))
        sys.exit(display_usage(-1))

    for o, a in opts:
        if o in ("-h", "--help"):
            sys.exit(display_usage(0))

        if o in ("-v", "--version"):
            sys.exit(display_version())

        if o in ("-r", "--resp"):
            show_resp = True

        if o in ("-c", "--colorless"):
            colors = False

        if o in ("-p", "--port"):
            try:
                port = int(a)

            except ValueError:
                print('Error: Invalid port number entered: ' + a)
                sys.exit(display_usage(-1))

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            display_header(no_prompt=False, colors=colors)
            get_conn(s)

            while True:
                command: str = input('{}:{}> '.format(host, port))
                execute(command, s, host, port, colors, show_resp)

    except ConnectionRefusedError:
        display_version()
        print_gray('ERROR: Could not connect to Redis server. Is it running?', colors)
        print()
        sys.exit(-1)

    except KeyboardInterrupt:
        exit_client(s)
        sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])
