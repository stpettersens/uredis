# $server:client

import os
import platform

def is_windows() -> bool:
    if platform.system() == 'Windows':
        return True

    return False

def is_unix_like() -> bool:
    if platform.system() == 'Linux':
        return True
    elif platform.system() == 'Darwin':
        return True
    elif platform.system().find('BSD') != -1:
        return True

    return False

def get_platform() -> str:
    return platform.system()

def get_arch() -> str:
    return platform.machine().lower()

def get_os() -> str:
    return f'{get_platform()} {platform.release()} {get_arch()}'

def get_arch_bits() -> str:
    if platform.machine().endswith('64'):
        return '64'

    return '32'

def clear_screen() -> None:
    if is_windows():
        os.system('cls')
    elif is_unix_like():
        os.system('clear')
    else:
        os.system('clear')
