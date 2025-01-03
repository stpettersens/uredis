# $server

from itertools import count

class Connections:
    cid = count(1)
    cids: dict[str, int] = {}

    def set(self, peer_name: tuple[str, str]) -> None:
        self._cid: int = next(self.cid)
        self.cids[peer_name[1]] = self._cid

    def get(self, peer_name: tuple[str, str]) -> int:
        return self.cids[peer_name[1]]

    def all(self) -> dict[str, int]:
        return self.cids
