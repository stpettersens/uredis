# $client

from itertools import count

from resp.resp_type import RespType

class RespDecoder:
    def __init__(self, response: bytes, command: bytes = b'') -> None:
        self.response: str = response.decode('utf-8')
        self.command: str = command.decode('utf-8')

    def decode(self) -> (str, RespType):
        if self.command.find('INFO') != -1:
            out: list[str] = self.response.split('\r\n')
            out.pop(0)
            return ('\r\n'.join(out), RespType.INFO)

        if self.response[0] == '+':
            return (self.response[1:].strip(), RespType.STATUS)

        elif self.response[0] == '-':
            return ("(error) {}".format(self.response[1:].strip()), RespType.ERROR)

        elif self.response[0] == ':':
            return (self.response[1:].strip(), RespType.NUMBER)

        elif self.response[0] == '*':
            out: list[str] = []
            keys: list[str] = self.response.split('\r\n')
            keys.pop(0)
            n: int = 1
            for k in keys:
                if k.startswith('$'):
                    continue
                if k.startswith(':'):
                    out.append('{}) (integer) {}'.format(n, k[1:]))

                elif k.startswith('*'):
                    if k[1:] == '0':
                        out.append('{}) (empty array)'.format(n))
                else:
                    out.append('{}) "{}"'.format(n, k))
                n += 1

            out.pop()
            if len(out) == 0:
                out.append('(empty array)')

            return ('\r\n'.join(out), RespType.KEYS)

        elif self.response[0] == '%':
            out: list[str] = []
            _keys: list[str] = []
            keys: list[str] = self.response.split('\r\n')
            keys.pop(0)
            for k in keys:
                if k.startswith('$'):
                    continue
                else:
                    _keys.append(k)

            n: int = 1
            for nn in count(start=0, step=2):
                if (nn + 1) == len(_keys):
                    break

                o: str = '{}# "{}" => '.format(n, _keys[nn])
                if _keys[(nn + 1)].startswith(':'):
                    o += '(integer) {}'.format(_keys[(nn + 1)][1:])

                elif _keys[(nn + 1)].startswith('*'):
                    if _keys[(nn + 1)][1:] == '0':
                        o += '(empty array)'
                else:
                    o += '"{}"'.format(_keys[(nn + 1)])

                out.append(o)
                n += 1

            return ('\r\n'.join(out), RespType.KEYVALS)


        elif self.response[0] == '$':
            decoded: str = self.response.split('\r\n')[1].strip()
            decoded = '"{}"'.format(decoded)
            return (decoded, RespType.STRING)
