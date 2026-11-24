"""여러 서버가 같이 쓰는 카운터(Redis 흉내): 읽고 쓰기를 따로 하면 경쟁이 생긴다."""


class Store:
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key, 0)

    def set(self, key, value):
        self.data[key] = value

    def incr(self, key):
        """한 번에 더하고 새 값을 돌려준다(Redis INCR처럼 원자적)."""
        self.data[key] = self.data.get(key, 0) + 1
        return self.data[key]


def check_then_set(store, key, limit, n):
    """요청 n개가 동시에 와서 모두 먼저 읽고, 그다음 모두 쓴다(가장 나쁜 겹침)."""
    seen = [store.get(key) for _ in range(n)]          # 모두 같은 값을 읽음
    allowed = [v < limit for v in seen]
    for v, ok in zip(seen, allowed):
        if ok:
            store.set(key, v + 1)                      # 서로의 +1을 덮어씀
    return sum(allowed)


def incr_then_check(store, key, limit, n):
    return sum(store.incr(key) <= limit for _ in range(n))
