# $client

from enum import Enum

class RespType(Enum):
    STATUS = 0
    ERROR = 1
    NUMBER = 2
    KEYS = 3,
    KEYVALS = 4,
    STRING = 5,
    INFO = 6
