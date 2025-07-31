# $client

from enum import Enum

class RespType(Enum):
    EMPTY = -1
    STATUS = 0
    ERROR = 1
    NUMBER = 2
    KEYS = 3
    KEYVALS = 4
    STRING = 5
    INFO = 6
    SHOULD_NOT_SEND = 7
    DOCUMENTATION = 8
