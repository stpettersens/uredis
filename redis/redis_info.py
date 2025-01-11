# $server

import os
import sys

from time import time
from datetime import datetime, timedelta

from detection.detection import get_os, get_arch_bits, is_unix_like

def calculate_up_time(start_time: datetime) -> timedelta:
    return (datetime.now() - start_time)

def calculate_up_seconds(start_time: datetime) -> int:
    return calculate_up_time(start_time).seconds

def calculate_up_days(start_time: datetime) -> int:
    return calculate_up_time(start_time).days

class RedisInfo:
    def __init__(self, working_dir: str, version: str,
    num_conns: int, port: int, start_time: datetime) -> None:
        self.working_dir: str = working_dir
        self.version: str = version
        self.num_conns: int = num_conns
        self.port: int = port
        self.start_time: datetime = start_time

    def get(self, section: bytes = b'') -> bytes:
        ssection: str = section.decode('utf-8')
        match ssection.lower():
            case '':
                return self.get_all_sections()

            case 'server':
                return str.encode("${}\r\n{}".format(len(self.get_server_section()), self.get_server_section()))

            case 'clients':
                return str.encode("${}\r\n{}".format(len(self.get_clients_section()), self.get_clients_section()))

            case 'memory':
                return str.encode("${}\r\n{}".format(len(self.get_memory_section()), self.get_memory_section()))

        return self.get_all_sections()

    def get_all_sections(self) -> bytes:
        sections: str = '$5260\r\n{}\r\n\r\n{}\r\n\r\n{}\r\n'.format(self.get_server_section(), self.get_clients_section(), self.get_memory_section())

        return str.encode(sections)

    def get_memory_section(self) -> str:
        memory_kb: int = 0
        if is_unix_like():
            import resource
            memory_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        return """# Memory\r\nused_memory:{}\r\nused_memory_human:{}K\r\nused_memory_rss:{}\r\nused_memory_rss_human:{}M\r\n""".format((memory_kb * 1000), memory_kb, (memory_kb * 1000), (memory_kb / 1000))

    def get_clients_section(self) -> str:
        return """# Clients\r\nconnected_clients:{}\r\ncluster_connections:0\r\nmaxclients:10000\r\nclient_recent_max_input_buffer:0\r\nclient_recent_max_output_buffer:0\r\nblocked_clients:0\r\ntracking_clients:0\r\nclients_in_timeout_table:0""".format(self.num_conns)

    def get_server_section(self) -> str:
        uptime_secs: int = calculate_up_seconds(self.start_time)
        uptime_days: int = calculate_up_days(self.start_time)

        return """# Server\r\nredis_version:{}\r\nredis_git_sha1:00000000\r\nredis_git_dirty:0\r\nredis_build_id:d81bff71cbf150e\r\nredis_mode:standalone\r\nos:{}\r\narch_bits:{}\r\nmonotonic_clock:POSIX clock_gettime\r\nmultiplexing_api:epoll\r\natomicvar_api:c11-builtin\r\ngcc_version:Python {}\r\nprocess_id:{}\r\nprocess_supervised:no\r\nrun_id:0\r\ntcp_port:{}\r\nserver_time_usec:{}\r\nuptime_in_seconds:{}\r\nuptime_in_days:{}\r\nhz:10\r\nconfigured_hz:10\r\nlru_clock:0\r\nexecutable:{}\r\nconfig_file:\r\nio_threads_active:0""".format(self.version, get_os(), get_arch_bits(), sys.version, os.getpid(), self.port, int((time() * 1e6)), uptime_secs, uptime_days, self.working_dir)
