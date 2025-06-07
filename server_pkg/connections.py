# $server

from itertools import count

class Connections:
    cid = count(1)
    cids: dict[int, int] = {}

    def set(self, peer_name: tuple[str, str]) -> None:
        self._cid: int = next(self.cid)
        self.cids[int(peer_name[1])] = self._cid

    def as_bytes(self, peer_name: tuple[str, str]) -> bytes:
        return str.encode(f'{peer_name[0]}:{peer_name[1]}\r\n')

    def from_bytes(self, peer_name: bytes) -> tuple[str, str]:
        kv: list[str] = peer_name.decode('utf-8').split(':')
        kv[1] = kv[1].split('\\')[0]
        return (kv[0], kv[1])

    def get(self, peer_name: tuple[str, str]) -> int:
        return self.cids[int(peer_name[1])]

    def drop(self, peer_name: tuple[str, str]) -> str:
        self.cids[int(peer_name[1])] = 0
        return f"Dropped connection {peer_name[1]}."

    def get_count(self) -> int:
        conns: int = 0
        for v in self.cids.values():
            if int(v) > 0:
                conns += 1

        return conns

    def all(self) -> dict[int, int]:
        return self.cids
