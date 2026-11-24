"""연습 문제 풀이: 사용자마다 토큰 통 하나, 응답에 429 · Retry-After · 남은 횟수 헤더 붙이기
python3 solutions/headers.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from limiters import TokenBucket  # noqa: E402


class Gateway:
    def __init__(self, capacity, rate, clock):
        self.capacity, self.rate, self.clock, self.buckets = capacity, rate, clock, {}

    def handle(self, user):
        tb = self.buckets.setdefault(user, TokenBucket(self.capacity, self.rate, self.clock))
        if tb.allow():
            return 200, {"X-RateLimit-Limit": self.capacity, "X-RateLimit-Remaining": int(tb.tokens)}
        return 429, {"X-RateLimit-Limit": self.capacity, "X-RateLimit-Remaining": 0, "Retry-After": tb.retry_after()}


if __name__ == "__main__":
    t = [0.0]
    gw = Gateway(3, 0.5, lambda: t[0])
    for user in ["kim", "kim", "kim", "kim", "lee"]:
        print(user, *gw.handle(user))
    t[0] = 2.0
    print("2초 뒤 kim", *gw.handle("kim"))
