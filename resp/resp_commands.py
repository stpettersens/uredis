# $server:client

# Supported commands are listed below:
class RespCommands:
    def get(self) -> list[str]:
        return [
            '_get_conn', # since v0.2.0
            'HELLO',
            'INFO',      # since v0.2.0
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
