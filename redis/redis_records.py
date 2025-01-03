# $server

import uuid

from typing import TypeAlias

from redis.redis_record import RedisRecord

UUID: TypeAlias = uuid.UUID

class RedisRecords:
    def __init__(self) -> None:
        self.uuid: UUID = uuid.uuid4()
        self.records: dict = {}

    def _update_uuid(self) -> None:
        # We call this method whenever we
        # push records or delete records.
        self.uuid = uuid.uuid4()

    def has_changed(self, _uuid: UUID) -> bool:
        if self.uuid != _uuid:
            return True

        return False

    def get_uuid(self) -> UUID:
        return self.uuid

    def get_number(self) -> int:
        return len(self.records)

    def push_record(self, key: bytes, record: RedisRecord):
        self._update_uuid()
        self.records[str(key)] = record

    def get_record(self, key: str|bytes) -> RedisRecord:
        if not str(key) in self.records:
            return RedisRecord(b'', dummy=True)
        else:
            return self.records[str(key)]

    def delete_all_records(self) -> bytes:
        self._update_uuid()
        self.records = {}
        return b'+OK\r\n'

    def delete_record(self, key: str|bytes) -> bytes:
        if not str(key) in self.records:
            return b':0\r\n'

        self._update_uuid()
        del self.records[str(key)]
        return b':1\r\n'

    def get_keys(self) -> list[str]:
        keys = list(self.records.keys())
        return keys

    def get_keys_as_bytes(self) -> bytes:
        keys = self.get_keys()
        if len(keys) == 0:
            return b'*0\r\n'
        else:
            kk: str = '*{}\r\n'.format(len(keys))
            for k in keys:
                kk += '${}\r\n'.format(len(k[2:-1]))
                kk += '{}\r\n'.format(k[2:-1])

            return str.encode(kk)
