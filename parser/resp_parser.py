# $server

# RESP Message Parser
from resp.resp_commands import RespCommands
from tokenizer.resp_token import Token, TokenKind
from tokenizer.resp_tokenizer import Tokenizer

class Parser:
    def __init__(self, resp_str: str) -> None:
        self.commands: dict[str, tuple[str, str]] = RespCommands().get()
        self.tokens: list[Token] = []

        toks = Tokenizer(resp_str).get_tokens()
        toks.pop(0) # Pop off first token.

        groups: list[int] = []
        cmds: list[str] = []

        for t in toks:
            if t.kind() == TokenKind.LENGTH:
                groups.append(int(t.value()))

            elif t.kind() == TokenKind.CMDPARAM:
                cmds.append(t.value())

            elif t.kind() == TokenKind.PARAMSPACE:
                cmds.append(t.value())

            elif t.kind() == TokenKind.PARAMWILDCARD:
                cmds.append(t.value())

        for g in groups:
            temp = []
            for n in range(0, g):
                temp.append(cmds.pop(0)) # Pop off first value.

            value: str = ''.join(temp)

            if value in self.commands.keys():
                self.tokens.append(Token(TokenKind.CMD, value))
            else:
                self.tokens.append(Token(TokenKind.PARAM, value))

    def get_tokens(self) -> list[Token]:
        return self.tokens

    def each_token(self) -> None:
        for t in self.tokens:
            print("{} ({})".format(t.kind(), t.value()))
