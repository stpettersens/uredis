# $server

from enum import Enum

class TokenKind(Enum):
    NUMBER = 0
    LENGTH = 1
    CMDPARAM = 2
    CMD = 3
    PARAM = 4
    PARAMSPACE = 5
    PARAMWILDCARD = 6
    SPACE = 7

class Token:
    def __init__(self, kind: TokenKind, value: str) -> None:
        self.tok_kind: TokenKind = kind
        self.tok_value: str = value

    def __repr__(self) -> str:
        return '{} [{}]'.format(self.tok_kind, self.tok_value)

    def kind(self) -> TokenKind:
        return self.tok_kind

    def value(self) -> str:
        return self.tok_value
