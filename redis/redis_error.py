# $server

class RedisError:
    def __init__(self, message: str|ValueError) -> None:
        self.message: str|ValueError = message

    def get(self) -> bytes:
        return str.encode('-ERR {}\r\n'.format(self.message))
