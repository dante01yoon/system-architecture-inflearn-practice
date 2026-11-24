"""python3 demo.py 1 → 창 경계 몰림,  2 → 토큰 통 다시 차기,  3 → 두 서버가 같은 카운터를 쓸 때"""
import random
import sys
import unicodedata

from limiters import FixedWindow, LeakyBucket, SlidingCounter, SlidingLog, TokenBucket
from store import Store, check_then_set, incr_then_check


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def pad(s, w):
    return s + " " * (w - sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s))


def boundary():
    rnd = random.Random(7)
    trace = sorted([rnd.uniform(55, 60) for _ in range(12)] + [rnd.uniform(60, 65) for _ in range(12)])
    print("1) 한도: 60초에 10번 · 요청 24개(55~60초에 12개, 60~65초에 12개, seed 7)")
    print(f"   {pad('알고리즘', 18)}55~60초  60~65초  10초 합계")
    for name, make in [("fixed window", lambda c: FixedWindow(10, 60, c)), ("sliding log", lambda c: SlidingLog(10, 60, c)),
                       ("sliding counter", lambda c: SlidingCounter(10, 60, c)), ("token bucket", lambda c: TokenBucket(10, 10 / 60, c)),
                       ("leaky bucket", lambda c: LeakyBucket(10, 10 / 60, c))]:
        clock = Clock(); lim = make(clock); a = b = 0
        for t in trace:
            clock.t = t
            if lim.allow():
                a, b = (a + 1, b) if t < 60 else (a, b + 1)
        print(f"   {pad(name, 18)}{a:>5}    {b:>5}    {a + b:>6}")
    print("2) fixed window만 경계 양쪽 10초에 한도의 2배를 통과시킨다")


def refill():
    clock = Clock()
    tb = TokenBucket(5, 1.0, clock)
    print("1) 토큰 통: 최대 5개 · 1초에 1개씩 다시 찬다")
    clock.t = 0.0
    burst = [tb.allow() for _ in range(7)]
    print(f"   0.0초  요청 7개 몰림 → 허용 {sum(burst)} · 거절 {7 - sum(burst)}   Retry-After: {tb.retry_after()}")
    for t in (0.5, 1.0, 2.5, 3.0, 3.2, 8.0):
        clock.t = t
        tb._refill(); before = tb.tokens
        ok = tb.allow()
        extra = "" if ok else f"   Retry-After: {tb.retry_after()}"
        print(f"   {t:>3.1f}초  토큰 {before:3.1f} → {'허용' if ok else '거절'}{extra}")
    print("2) 오래 쉬어도 토큰은 5개까지만 찬다 · 몰림 크기 = 통 크기")


def race():
    print("1) 서버 두 대가 같은 카운터를 쓴다 · 한도 10 · 요청 20개가 동시에")
    print(f"   읽고 비교하고 쓰기(GET → SET)   통과 {check_then_set(Store(), 'ip:1', 10, 20)}개")
    print(f"   한 번에 더하기(INCR)            통과 {incr_then_check(Store(), 'ip:1', 10, 20)}개")
    print("2) 읽기와 쓰기 사이에 다른 요청이 끼면 서로의 +1을 덮어쓴다")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "1"
    {"1": boundary, "2": refill, "3": race}[arg]()
