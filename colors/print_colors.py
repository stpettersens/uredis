# $server:client

def print_green(message: str, colors: bool) -> None:
    if colors:
        print("\033[32m{}\033[0m".format(message))
    else:
        print(message)

def print_yellow(message: str|bytes, colors: bool) -> None:
    if colors:
        print("\033[33m{}\033[0m".format(message))
    else:
        print(message)

def print_cyan(message: str, colors: bool) -> None:
    if colors:
        print("\033[36m{}\033[0m".format(message))
    else:
        print(message)

def print_magenta(message: str, colors: bool) -> None:
    if colors:
        print("\033[35m{}\033[0m".format(message))
    else:
        print(message)

def print_red(message: str, colors: bool) -> None:
    if colors:
        print("\033[31m{}\033[0m".format(message))
    else:
        print(message)

def print_gray(message: str, colors: bool, pattern: str = '') -> None:
    if colors:
        if pattern == '':
            print("\033[90m{}\033[0m".format(message))
        else:
            for msg in message.split('\r\n'):
                mm: list[str] = msg.split(pattern, 1)
                print("\033[90m{}{}\033[0m{}".format(mm[0], pattern, mm[1]))
    else:
        print(message)
