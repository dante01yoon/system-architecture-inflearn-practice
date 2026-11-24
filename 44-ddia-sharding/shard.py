"""샤딩: 키 범위 대 해시, 해시 mod N 재균형, 인기 키 salting (서점 주문, 파이썬 표준 라이브러리만)."""
import datetime as dt
import hashlib
import random

DAY0 = dt.date(2026, 10, 15)   # 지난 30일: 10/15 ~ 11/13, 오늘 = 11/14


def orders(n=20_000, seed=7):
    """서점 주문 n건: (주문 번호, 주문 날짜, 작가). 날짜는 지난 30일에 고르게."""
    rnd = random.Random(seed)
    authors = [f"작가{i:03d}" for i in range(300)]
    return [(f"o{100000 + i}", DAY0 + dt.timedelta(days=rnd.randrange(30)), rnd.choice(authors)) for i in range(n)]


def today_orders(n=1_000, start=200_000):
    return [(f"o{start + i}", DAY0 + dt.timedelta(days=30), "") for i in range(n)]


def h(key):
    """키의 해시(파이썬 hash()는 실행마다 바뀌어서 md5를 쓴다)."""
    return int.from_bytes(hashlib.md5(key.encode()).digest()[:8], "big")


def range_bounds(keys, shards):
    """키 범위 샤딩: 키를 정렬해 개수가 같도록 경계를 잡는다. 마지막 샤드는 끝이 열려 있다."""
    s = sorted(keys)
    return [s[len(s) * k // shards] for k in range(1, shards)]


def by_range(key, bounds):
    return sum(key >= b for b in bounds)


def by_hash(key, shards):
    return h(key) % shards


def count(shard_ids, shards):
    c = [0] * shards
    for s in shard_ids:
        c[s] += 1
    return c


def moved_mod_n(keys, old, new):
    """해시 mod N: 샤드 수가 old → new로 바뀔 때 다른 샤드로 옮겨야 하는 키의 비율."""
    return sum(h(k) % old != h(k) % new for k in keys) / len(keys)


def assign(partitions, nodes, new_nodes=0):
    """파티션 수는 고정. 노드가 늘면 가장 많이 가진 노드가 파티션을 하나씩 넘겨준다(나머지는 제자리)."""
    owner = {p: p % nodes for p in range(partitions)}
    for n in range(nodes, nodes + new_nodes):
        for _ in range(partitions // (n + 1)):
            have = [sum(o == k for o in owner.values()) for k in range(n)]
            rich = have.index(max(have))
            owner[max(p for p, o in owner.items() if o == rich)] = n
    return owner


def moved_fixed(keys, partitions, old, new):
    """고정 파티션: 키 → 파티션은 그대로, 파티션 → 노드만 바뀐다. (옮긴 키 비율, 옮긴 파티션 수)"""
    a, b = assign(partitions, old), assign(partitions, old, new - old)
    moved_p = {p for p in range(partitions) if a[p] != b[p]}
    return sum(h(k) % partitions in moved_p for k in keys) / len(keys), len(moved_p)


def salted(key, rnd, fan=16):
    """인기 키 뒤에 0~fan-1 숫자를 붙여 여러 샤드로 흩는다."""
    return f"{key}#{rnd.randrange(fan)}"
