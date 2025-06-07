# $client

from resp.resp_commands import RespCommands

class RespEncoder:
    def __init__(self, command: str) -> None:
        self.commands: list[str] = RespCommands().get()
        self.command: str = command

    def encode(self) -> list[bytes]:
        encodeds: list[bytes] = []
        for cmd in self.command.split(';'):
            formatted: list[str] = []
            look_for_command: bool = True # Look for command.
            for part in cmd.split(' '):
                formatted.append('${}'.format(len(part)))
                if look_for_command and part.upper() in self.commands:
                    formatted.append(part.upper())
                    look_for_command = False
                else:
                    formatted.append(part)

            encoded: str = '*1' + '\r\n' + '\r\n'.join(formatted) + '\r\n'

            if encoded.find('$0') == -1: # Ignore empty commands caused by ';'
                encodeds.append(str.encode(encoded))

        return encodeds
