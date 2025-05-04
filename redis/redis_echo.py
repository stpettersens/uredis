# $server

from redis.redis_command import RedisCommand

class RedisEcho(RedisCommand):
    def get(self) -> bytes:
        msg: str = '${}\r\n{}\r\n'.format(len(self.message[2:-1]), self.message[2:-1])
        return str.encode(msg)
