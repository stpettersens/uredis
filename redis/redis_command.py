# $server

from abc import abstractmethod

class RedisCommand:
    def __init__(self, message: bytes) -> None:
        self.message: str = str(message).replace('___', ' ')

    @abstractmethod
    def get(self) -> bytes:
        pass
