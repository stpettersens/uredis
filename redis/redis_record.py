# $server

from typing import final

@final
class RedisRecord:
    __slots__ = ('record', 'ttl', 'dummy')

    def __init__(self, value: bytes, ttl: int = -1, dummy: bool = False) -> None:
        self.record = str(value).replace('___', ' ')
        self.ttl = ttl
        self.dummy = dummy

    def is_dummy(self) -> bool:
        return self.dummy

    def ok(self) -> bytes:
        return b'+OK\r\n'

    def get(self) -> bytes:
        return str.encode('${}\r\n{}\r\n'
        .format(len(self.record[2:-1]), self.record[2:-1]))

    def decrement_ttl(self) -> None:
        self.ttl += -1

    def get_ttl(self) -> int:
        return self.ttl

    def get_ttl_as_bytes(self) -> bytes:
        return str.encode(':{}\r\n'.format(self.ttl))
