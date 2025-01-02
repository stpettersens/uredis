# $server:client

# Supported commands are listed below:
class RespCommands:
    def get(self) -> list[str]:
        return [
            'HELLO',
            'INFO', # since v0.2.0
            'CLIENT',
            'PING',
            'ECHO',
            'SET',
            'GET',
            'TTL',
            'DEL',
            'FLUSHDB',
            'FLUSHALL',
            'KEYS'
        ]
