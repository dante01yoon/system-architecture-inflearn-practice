"""count-min sketch: 줄 d개 × 칸 w개. 책마다 줄마다 칸 하나를 올리고, 읽을 땐 그 칸들 중 가장 작은 값."""
import hashlib


class CountMin:
    def __init__(self, width=2000, depth=4):
        self.w, self.d = width, depth
        self.rows = [[0] * width for _ in range(depth)]

    def _cols(self, item):
        for i in range(self.d):
            h = hashlib.blake2b(f"{i}:{item}".encode(), digest_size=8).digest()
            yield i, int.from_bytes(h, "big") % self.w

    def add(self, item, n=1):
        for i, c in self._cols(item):
            self.rows[i][c] += n

    def query(self, item):
        return min(self.rows[i][c] for i, c in self._cols(item))   # 겹친 몫이 가장 적은 칸
