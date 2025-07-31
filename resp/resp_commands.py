# $server:client

# Supported commands with some usage definitions are listed below.
# Commands that should not be used directly by the client begin with an underscore ('_').

# IMPL is a non-standard Redis command implemented to display usage definition for a command
# when user client sends IMPL [command_in_lowercase] to the server.

# <blah> indicates parameter that must be provided to a command.
# [blah] indicates optional parameter for a command.
class RespCommands:
    def get(self) -> dict[str, tuple[str, str]]:
        return {
            '_GET_CONN': ('', ''), # Get a connection, should not be used directly by client.
            '_DROP_CONN':('', ''), # Drop a connection, should not be used directly by client.

            # The following commands can and should be used by the client.
            'HELLO':   ('HELLO <proto_ver>', 'Switch to a different protocol version (2 or 3)'),
            'INFO':    ('INFO [section]', 'Display all server information or for given section'),
            'CLIENT':  ('CLIENT', 'Set the client on the server (only partially implemented)'),
            'PING':    ('PING [message]', 'Ping the server which responds with PONG or echoes message'),
            'ECHO':    ('ECHO <message>', 'Server echoes the provided message'),
            'EXISTS':  ('EXISTS <key>, [...]', 'Increments return integer for each key that exists or 0'),
            'SET':     ('SET <key> <value>', 'Stores key and value as record in database'),
            'GET':     ('GET <key>', 'Get the record at key from database or returns ""'),
            'TTL':     ('TTL <key>', 'Returns TTL for a key, -1 for infinite or -2 for non-existent'),
            'DEL':     ('DEL <key>', 'Delete a record from database'),
            'FLUSHDB': ('FLUSHDB', 'Flush database of all records'),
            'FLUSHALL':('FLUSHALL', 'Flush database of all records'),
            'KEYS':    ('KEYS <*>', 'Get list of all keys from database'),
            'QUIT':    ('QUIT', 'Close connection to the server and exit client as applicable'),
            'IMPL':    ('IMPL [command_in_lowercase]',
                        'Get all implemented commands or usage for given command provided in lowercase')
        }
