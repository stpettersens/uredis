# $server

from threading import Event

from server_pkg.logs import Logs
from redis.redis_records import RedisRecords

class ExitParams:
    def __init__(self, working_dir: str, records: RedisRecords,
    stop_event: Event, dump_db: bool, no_disk: bool, max_size: int, logs: Logs, log_file: str) -> None:
        self.working_dir: str = working_dir
        self.records: RedisRecords = records
        self.stop_event: Event = stop_event
        self.dump_db: bool = dump_db
        self.no_disk: bool = no_disk
        self.max_size: int = max_size
        self.logs: Logs = logs
        self.log_file: str = log_file
