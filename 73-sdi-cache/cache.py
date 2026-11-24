"""LRU 캐시(TTL 포함)와 캐시 앞의 요청 몰림 막기(single-flight). 표준 라이브러리만."""
import math
import random
import threading
import time
from collections import OrderedDict


class LRU:
    """가장 오래 안 쓴 것부터 내보내는 캐시. ttl초가 지난 값은 없는 것으로 친다."""

    def __init__(self, size, ttl=None, clock=time.monotonic):
        self.size, self.ttl, self.clock = size, ttl, clock
        self.data = OrderedDict()            # 키 → (값, 만료 시각), 뒤쪽이 최근
        self.hits = self.misses = 0

    def get(self, key):
        item = self.data.get(key)
        if item is None or (item[1] is not None and self.clock() >= item[1]):
            self.data.pop(key, None)
            self.misses += 1
            return None
        self.data.move_to_end(key)           # 방금 썼다 → 맨 뒤로
        self.hits += 1
        return item[0]

    def put(self, key, value, ttl=None):
        ttl = self.ttl if ttl is None else ttl
        self.data[key] = (value, None if ttl is None else self.clock() + ttl)
        self.data.move_to_end(key)
        if len(self.data) > self.size:
            self.data.popitem(last=False)    # 맨 앞 = 가장 오래 안 쓴 것

    def ratio(self):
        return self.hits / max(1, self.hits + self.misses)


def zipf_keys(n_keys, n_req, s=1.0, seed=7):
    """인기 순위 k번 키가 1/k^s 비율로 불리는 요청 줄(몇몇 키에 몰린다)."""
    w = [1 / (k ** s) for k in range(1, n_keys + 1)]
    return random.Random(seed).choices(range(n_keys), weights=w, k=n_req)


class Origin:
    """느린 원본(DB). 몇 번 불렸는지 센다."""

    def __init__(self, delay=0.05):
        self.delay, self.calls, self.lock = delay, 0, threading.Lock()

    def load(self, key):
        with self.lock:
            self.calls += 1
        time.sleep(self.delay)
        return f"value-{key}"


def read(cache, origin, key):
    """cache-aside: 없으면 원본에서 읽어 채운다. 동시에 비면 모두 원본으로 간다."""
    value = cache.get(key)
    if value is None:
        value = origin.load(key)
        cache.put(key, value)
    return value


_locks, _guard = {}, threading.Lock()


def read_once(cache, origin, key):
    """single-flight: 키마다 자물쇠 하나. 처음 온 요청만 원본에 가고, 나머지는 기다렸다가 채워진 값을 읽는다."""
    value = cache.get(key)
    if value is not None:
        return value
    with _guard:
        lock = _locks.setdefault(key, threading.Lock())
    with lock:
        value = cache.get(key)               # 기다리는 동안 누가 채웠나?
        if value is None:
            value = origin.load(key)
            cache.put(key, value)
    return value


def jitter_ttl(base, spread, rnd):
    """TTL에 ±spread 비율의 흔들림을 더해 만료 시각을 흩는다."""
    return base * (1 + rnd.uniform(-spread, spread))


def early(now, expiry, delta, beta=1.0, rnd=random):
    """확률적 조기 만료(Vattani 외 2015, XFetch): 만료가 가까울수록, 다시 계산이 오래 걸릴수록 일찍 새로 고칠 확률이 커진다."""
    return now - delta * beta * math.log(rnd.random()) >= expiry
