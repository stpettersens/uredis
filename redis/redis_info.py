# $server

import os
import sys
import pickle
from time import time
from typing import TypeAlias
from datetime import datetime

from detection.detection import get_os, get_arch_bits

DateTime: TypeAlias = datetime

class RedisInfo:
    def __init__(self, version: str, port: int) -> None:
        self.version: str = version
        self.port: int = port

    def get(self, section: bytes = b'') -> bytes:
        ssection: str = section.decode('utf-8')

        if ssection.lower() == 'server':
            return str.encode("${}\r\n{}"
            .format(len(self.get_server_section()), self.get_server_section()))

        return self.get_all_sections()

    def get_all_sections(self) -> bytes:
        sections: str = '$5260\r\n{}'.format(self.get_server_section())
        return str.encode(sections)

    def get_server_section(self) -> str:
        return """# Server\r\nredis_version:{}\r\nredis_git_sha1:00000000\r\nredis_git_dirty:0\r\nredis_build_id:d81bff71cbf150e\r\nredis_mode:standalone\r\nos:{}\r\narch_bits:{}\r\nmonotonic_clock:POSIX clock_gettime\r\nmultiplexing_api:epoll\r\natomicvar_api:c11-builtin\r\ngcc_version:Python {}\r\nprocess_id:{}\r\nprocess_supervised:no\r\nrun_id:0\r\ntcp_port:{}\r\nserver_time_usec:{}\r\nuptime_in_seconds:{}""".format(self.version, get_os(), get_arch_bits(), sys.version, os.getpid(), self.port, int(time() * 1e6), 0)
