# $server:client

# Supported commands are listed below.
# Non-standard Redis commands begin with an underscore ('_'):
class RespCommands:
    def get(self) -> list[str]:
        return [
            'HELLO',
            'INFO',         # since v0.2.0
            'CLIENT',
            'PING',
            'ECHO',
            'EXISTS',       # since v0.2.0
            'SET',
            'GET',
            'TTL',
            'DEL',
            'FLUSHDB',
            'FLUSHALL',
            'KEYS',
            '_GET_CONN',    # since v0.2.0
            '_DROP_CONN',   # since v0.2.0
            'QUIT'          # since v0.2.0, alias for _DROP_CONN
        ]
