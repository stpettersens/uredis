# $server

class RedisError:
    def __init__(self, message: str) -> None:
        self.message: str = message

    def get(self) -> bytes:
        return str.encode('-ERR {}\r\n'.format(self.message))
