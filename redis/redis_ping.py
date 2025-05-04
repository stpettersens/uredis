# $server

from redis.redis_command import RedisCommand

class RedisPing(RedisCommand):
    def __init__(self, message: bytes):
        self.message: str = '+PONG\r\n'
        if len(message) > 0:
            super().__init__(message)

    def get(self) -> bytes:
        if self.message != '+PONG\r\n':
            msg: str = '${}\r\n{}\r\n'.format(len(self.message[2:-1]), self.message[2:-1])
            return str.encode(msg)

        return str.encode(self.message)
