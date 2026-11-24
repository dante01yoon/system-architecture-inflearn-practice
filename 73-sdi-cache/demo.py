"""python3 demo.py 1 → 캐시 크기와 적중률,  2 → 만료 순간 요청 100개,  3 → TTL 흔들기"""
import random
import sys
import threading
import unicodedata
from collections import Counter

from cache import LRU, Origin, jitter_ttl, read, read_once, zipf_keys

CACHE_MS, DB_MS = 1, 20   # 가정: 캐시 1ms, DB 20ms


def pad(s, w):
    return s + " " * (w - sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s))


def hit_ratio():
    reqs = zipf_keys(10_000, 100_000)
    print("1) 키 10,000개 · 요청 100,000번 · 인기 키에 몰림")
    for size in (10, 100, 1_000, 5_000):
        c = LRU(size)
        for k in reqs:
            if c.get(k) is None:
                c.put(k, k)
        h = c.ratio()
        avg = h * CACHE_MS + (1 - h) * DB_MS
        print(f"   크기 {size:>5,} ({size / 100:>4.1f}%)  적중률 {h:6.1%}  평균 {avg:4.1f}ms")
    print("2) 평균 = 적중률 × 1ms + (1 − 적중률) × 20ms")


def stampede():
    print("1) 인기 키가 막 만료됐다 · 동시에 요청 100개")
    for label, fn in [("그냥 cache-aside", read), ("single-flight", read_once)]:
        cache, origin = LRU(100, ttl=60), Origin(delay=0.2)
        cache.put("best-seller", "old", ttl=0)   # 방금 만료된 값
        start = threading.Barrier(100)

        def worker():
            start.wait()
            fn(cache, origin, "best-seller")

        ts = [threading.Thread(target=worker) for _ in range(100)]
        [t.start() for t in ts]
        [t.join() for t in ts]
        print(f"   {pad(label, 18)} 원본 호출 {origin.calls:>3}번")
    print("2) 자물쇠 하나로 같은 키는 한 번만 원본에 간다")


def jitter():
    rnd = random.Random(7)
    print("1) 키 1,000개를 같은 순간에 채움 · TTL 60초")
    for label, spread in [("흔들기 없음", 0.0), ("±10% 흔들기", 0.1)]:
        per_sec = Counter(int(jitter_ttl(60, spread, rnd)) for _ in range(1_000))
        print(f"   {pad(label, 12)} 만료가 몰린 1초 최대 {max(per_sec.values()):>5,}개 · {len(per_sec)}초에 퍼짐")
    print("2) 만료 시각을 흩으면 원본이 한꺼번에 맞지 않는다")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "1"
    {"1": hit_ratio, "2": stampede, "3": jitter}[arg]()
