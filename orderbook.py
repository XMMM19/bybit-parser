# orderbook.py

from collections import OrderedDict

class OrderBook:
    def __init__(self):
        self.bids = OrderedDict()
        self.asks = OrderedDict()
        self.u = 0

    def apply_snapshot(self, snapshot: dict):
        self.bids = OrderedDict(
            sorted({float(p): float(s) for p, s in snapshot.get("b", [])}.items(), key=lambda x: -x[0])
        )
        self.asks = OrderedDict(
            sorted({float(p): float(s) for p, s in snapshot.get("a", [])}.items(), key=lambda x: x[0])
        )
        self.u = snapshot.get("u", 0)

    def apply_delta(self, delta: dict):
        for price_str, size_str in delta.get("b", []):
            price = float(price_str)
            size = float(size_str)
            if size == 0:
                self.bids.pop(price, None)
            else:
                self.bids[price] = size

        for price_str, size_str in delta.get("a", []):
            price = float(price_str)
            size = float(size_str)
            if size == 0:
                self.asks.pop(price, None)
            else:
                self.asks[price] = size

        self.bids = OrderedDict(sorted(self.bids.items(), key=lambda x: -x[0]))
        self.asks = OrderedDict(sorted(self.asks.items(), key=lambda x: x[0]))
        self.u = delta.get("u", self.u)

    def to_dict(self):
        return {
            "bids": [[str(p), str(s)] for p, s in self.bids.items()],
            "asks": [[str(p), str(s)] for p, s in self.asks.items()],
            "u": self.u
        }

    @classmethod
    def from_dict(cls, data: dict):
        ob = cls()
        ob.u = data.get("u", 0)
        ob.bids = OrderedDict(
            sorted({float(p): float(s) for p, s in data.get("bids", [])}.items(), key=lambda x: -x[0])
        )
        ob.asks = OrderedDict(
            sorted({float(p): float(s) for p, s in data.get("asks", [])}.items(), key=lambda x: x[0])
        )
        return ob
