# $server

# RESP Message Tokenizer
# Thanks to CodePulse on YouTube for guidance.
from tokenizer.resp_token import Token, TokenKind

class Tokenizer:
    def __init__(self, resp_str: str) -> None:
        parsed: list[str] = []
        for p in resp_str.split('\r\n'):
            if p.strip().startswith('*'):
                parsed.append(p.strip())
            else:
                parsed.append(p.replace(' ', chr(127)))

        parsed.pop() # Pop last element in parsed.

        self.resp_str: str = ' '.join(parsed).strip()
        self.curr_char: None|str = ''
        self.peek_char: None|str = ''
        self.tokens: list[Token] = []
        self.pos: int = -1

    def advance(self) -> None:
        self.pos += 1
        self.curr_char = self.resp_str[self.pos] if self.pos < len(self.resp_str) else None

    def peek(self) -> None:
        self.peek_char = self.resp_str[(self.pos + 1)] if (self.pos + 1) < len(self.resp_str) else None

    def each_token(self) -> None:
        for t in self.tokens:
            print("{} ({})".format(t.kind(), t.value()))

    def get_tokens(self) -> list[Token]:
        self.tokens = []

        while self.curr_char != None:
            if self.curr_char == ' ':
                self.tokens.append(Token(TokenKind.SPACE, self.curr_char))
                self.advance()

            elif self.curr_char == chr(127):
                self.tokens.append(Token(TokenKind.PARAMSPACE, '___'))
                self.advance()

            elif self.curr_char == '*':
                self.peek()
                if self.peek_char == None:
                    self.tokens.append(Token(TokenKind.PARAMWILDCARD, self.curr_char))
                    self.advance()
                else:
                    self.advance()
                    self.tokens.append(Token(TokenKind.NUMBER, self.curr_char))
                    self.advance()

            elif self.curr_char == '$':
                self.advance()
                if self.curr_char.isnumeric():
                    self.tokens.append(Token(TokenKind.LENGTH, self.curr_char))
                    self.advance()
                    while True:
                        if self.curr_char.isnumeric():
                            last: Token = self.tokens.pop() # Pop last token.
                            self.tokens.append(Token(TokenKind.LENGTH,
                            last.value() + self.curr_char))
                            self.advance()
                        else:
                            break

            else:
                self.tokens.append(Token(TokenKind.CMDPARAM, self.curr_char))
                self.advance()

        self.tokens.pop(0) # Pop first token.
        return self.tokens
