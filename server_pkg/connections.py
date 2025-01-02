# $server

from itertools import count

class Connections:
    cid: int = count(1)
    cids: dict = {}

    def set(self, peer_name: tuple) -> None:
        self.cid = next(self.cid)
        self.cids[peer_name[1]] = self.cid

    def get(self, peer_name: tuple) -> int:
        return self.cids[peer_name[1]]

    def all(self) -> dict:
        return self.cids
