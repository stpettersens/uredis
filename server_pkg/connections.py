# $server

from itertools import count
from _typeshed import SupportsNext

class Connections:
    cid: count[int] = count(1)
    cids: dict = {}

    def set(self, peer_name: tuple) -> None:
        self._cid: count[int] = next(self.cid)
        self.cids[peer_name[1]] = self._cid

    def get(self, peer_name: tuple) -> int:
        return self.cids[peer_name[1]]

    def all(self) -> dict:
        return self.cids
