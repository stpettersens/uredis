# $server

import os
import sys

from time import time
from datetime import datetime, timedelta

from redis.redis_records import RedisRecords
from detection.detection import get_os, get_arch_bits

def calculate_up_time(start_time: datetime) -> timedelta:
    return (datetime.now() - start_time)

def calculate_up_seconds(start_time: datetime) -> int:
    return calculate_up_time(start_time).seconds

def calculate_up_days(start_time: datetime) -> int:
    return calculate_up_time(start_time).days

class RedisInfo:
    def __init__(self, working_dir: str, version: str,
    num_conns: int, port: int, start_time: datetime, records: RedisRecords) -> None:
        self.working_dir: str = working_dir
        self.version: str = version
        self.num_conns: int = num_conns
        self.port: int = port
        self.start_time: datetime = start_time

# The Pympler module is an optional dependency so that we get dataset ("records") memory usage in INFO.
# Otherwise, we just return sys.getsizeof result for for dataset memory usages in bytes.
        records_size_func: str = """
from redis.redis_records import RedisRecords
try:
    from pympler import asizeof
except:
    pass

def get_records_memory_bytes(records: RedisRecords) -> int:
    try:
        return asizeof.asizeof(records)
    except:
        import sys

    return sys.getsizeof(records)

records_size: int = get_records_memory_bytes(records)"""

        params: dict[str, RedisRecords] = { 'records': records }
        locals_scope = dict(params)
        exec(records_size_func, {}, locals_scope)
        records_size = locals_scope['records_size']

        self.records_bytes = records_size
        print(f"The size of the records is {self.records_bytes} bytes.") # !!!

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
        #$5260
        sections: str = '$20000\r\n{}\r\n\r\n{}\r\n\r\n{}\r\n'.format(self.get_server_section(), self.get_clients_section(), self.get_memory_section())

        return str.encode(sections)

    def get_memory_section(self) -> str:
        mem_bytes: int = 0
        mem_peak: int = 0
        captured: dict[str, int] = {}

# The psuil module is an optional dependency so that we get process memory usage in INFO.
# Otherwise, we just return 0 for for memory usages in bytes.
        memory_funcs: str = """
from os import getpid
try:
    import psutil
except:
    pass

def get_memory_bytes() -> float:
    try:
        process = psutil.Process(getpid())
        return process.memory_info().rss
    except:
        pass

    return 0

def get_peak_memory_bytes() -> float:
    try:
        process = psutil.Process(getpid())
        return process.memory_info().peak_wset
    except:
        pass

    return 0

def get_system_memory_bytes() -> float:
    try:
        memory = psutil.virtual_memory()
        return memory.total
    except:
        pass

    return 0

mem_bytes: float = get_memory_bytes()
mem_peak: float = get_peak_memory_bytes()
tot_mem: float = get_system_memory_bytes()"""

        exec(memory_funcs, captured)
        mem_bytes = captured['mem_bytes']
        mem_peak = captured['mem_peak']
        tot_mem = captured['tot_mem']

        memory_kb: float = (mem_bytes / 1024) if mem_bytes != 0 else 0
        memory_mb: float = (mem_bytes / (1024 * 1024)) if mem_bytes != 0 else 0

        mem_peak_mb: float = (mem_peak / (1024 * 1024)) if mem_bytes != 0 and mem_peak != 0 else 0
        mem_peak_percent: float = ((mem_bytes / mem_peak) * 100) if mem_bytes != 0 and mem_peak != 0 else 0

        tot_mem_gb: float = (tot_mem / (1024 * 1024 * 1024)) if tot_mem != 0 else 0

        return """# Memory\r\nused_memory:{}\r\nused_memory_human:{}K\r\nused_memory_rss:{}\r\nused_memory_rss_human:{}M\r\nused_memory_peak:{}\r\nused_memory_peak_human:{}M\r\nused_memory_peak_perc:{}%\r\nused_memory_overhead:{}\r\nused_memory_startup:{}\r\nused_memory_dataset:{}\r\nused_memory_dataset_perc:{}%\r\nallocator_allocated:0\r\nallocator_active:0\r\ntotal_system_memory:{}\r\ntotal_system_memory_human:{}G\r\nused_memory_lua:0\r\nused_memory_vm_eval:0\r\nused_memory_lua_human:0.00K\r\nused_memory_scripts_eval:0\r\nnumber_of_cached_scripts:0\r\nnumber_of_functions:0\r\nnumber_of_libraries:0\r\nused_memory_vm_functions:0\r\nused_memory_vm_total:0\r\nused_memory_vm_total_human:0.00K\r\nused_memory_functions:0\r\nused_memory_scripts:0\r\nused_memory_scripts_human:0B\r\nmaxmemory:0\r\nmaxmemory_human:0B\r\nmaxmemory_policy:noeviction\r\nallocator_frag_ratio:0.00\r\nallocator_frag_bytes:0\r\nallocator_rss_ratio:0.00\r\nallocator_rss_bytes:0\r\nrss_overhead_ratio:0.00\r\nrss_overhead_bytes:0\r\nmem_fragmentation_ratio:0.00\r\nmem_fragmentation_bytes:0\r\nmem_not_counted_for_evict:0\r\nmem_replication_backlog:0\r\nmem_total_replication_buffers:0\r\nmem_clients_slaves:0\r\nmem_clients_normal:0\r\nmem_cluster_links:0\r\nmem_aof_buffer:0\r\nmem_allocator:jemalloc-5.3.0\r\nactive_defrag_running:0\r\nlazyfree_pending_objects:0\r\nlazyfreed_objects:0\r\n""".format(mem_bytes, f"{memory_kb:.2f}", mem_bytes, f"{memory_mb:.2f}", mem_peak, f"{mem_peak_mb:.2f}", f"{mem_peak_percent:.2f}", mem_bytes, mem_bytes, self.records_bytes, f"{mem_peak_percent:.2f}", tot_mem, f"{tot_mem_gb:.2f}")

    def get_clients_section(self) -> str:
        return """# Clients\r\nconnected_clients:{}\r\ncluster_connections:0\r\nmaxclients:10000\r\nclient_recent_max_input_buffer:0\r\nclient_recent_max_output_buffer:0\r\nblocked_clients:0\r\ntracking_clients:0\r\nclients_in_timeout_table:0""".format(self.num_conns)

    def get_server_section(self) -> str:
        uptime_secs: int = calculate_up_seconds(self.start_time)
        uptime_days: int = calculate_up_days(self.start_time)

        return """# Server\r\nredis_version:{}\r\nredis_git_sha1:00000000\r\nredis_git_dirty:0\r\nredis_build_id:d81bff71cbf150e\r\nredis_mode:standalone\r\nos:{}\r\narch_bits:{}\r\nmonotonic_clock:POSIX clock_gettime\r\nmultiplexing_api:epoll\r\natomicvar_api:c11-builtin\r\ngcc_version:Python {}\r\nprocess_id:{}\r\nprocess_supervised:no\r\nrun_id:0\r\ntcp_port:{}\r\nserver_time_usec:{}\r\nuptime_in_seconds:{}\r\nuptime_in_days:{}\r\nhz:10\r\nconfigured_hz:10\r\nlru_clock:0\r\nexecutable:{}\r\nconfig_file:\r\nio_threads_active:0""".format(self.version, get_os(), get_arch_bits(), sys.version[0:4], os.getpid(), self.port, int((time() * 1e6)), uptime_secs, uptime_days, self.working_dir)
