# $server

class RedisHello:
    def __init__(self, query_version: bytes, cid: int, server_version: str) -> None:
        self.str_query_version: str = query_version.decode('utf-8')
        self.server: str = 'uredis-server'
        self.version: int = 3
        self.proto: int = self.version
        self.cid: int = cid
        self.mode: str = 'standalone'
        self.role: str = 'master'
        self.modules: str = '*0'
        self.server_version: str = server_version

    def get(self) -> bytes:
        try:
            query_vers: int = int(self.str_query_version)
            if query_vers > self.version or query_vers < 2:
                raise ValueError

        except ValueError:
            return b'-NOPROTO unsupported protocol version.\r\n'

        if query_vers == self.version: # Version 3
            return str.encode(
"""%7\r\n$6\r\nserver\r\n${}\r\n{}\r\n$7\r\nversion\r\n${}\r\n{}\r\n$5\r\nproto\r\n:{}\r\n$2\r\nid\r\n:{}\r\n$4\r\nmode\r\n${}\r\n{}\r\n$4\r\nrole\r\n${}\r\n{}\r\n$7\r\nmodules\r\n{}\r\n"""
.format(
    len(self.server),
    self.server,
    len(self.server_version),
    self.server_version,
    self.proto,
    self.cid,
    len(self.mode),
    self.mode,
    len(self.role),
    self.role,
    self.modules
))

        # Version 2:
        return str.encode(
"""*14\r\n$6\r\nserver\r\n${}\r\n{}\r\n$7\r\nversion\r\n${}\r\n{}\r\n$5\r\nproto\r\n:{}\r\n$2\r\nid\r\n:{}\r\n$4\r\nmode\r\n${}\r\n{}\r\n$4\r\nrole\r\n${}\r\n{}\r\n$7\r\nmodules\r\n{}\r\n"""
.format(
    len(self.server),
    self.server,
    len(self.server_version),
    self.server_version,
    (self.proto - 1),
    self.cid,
    len(self.mode),
    self.mode,
    len(self.role),
    self.role,
    self.modules
))
