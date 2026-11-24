"""연습 풀이: 연속 실패 수 대신 최근 window번 중 실패 비율로 여는 브레이커(Fowler: 횟수 대신 비율도 된다)."""
import itertools
import time
from collections import deque


class RateBreaker:
    def __init__(self, rate=0.5, window=10, reset_timeout=10, clock=time.monotonic):
        self.rate, self.reset_timeout, self.clock = rate, reset_timeout, clock
        self.recent, self.state, self.opened_at = deque(maxlen=window), "closed", 0.0

    def call(self, fn, fallback):
        if self.state == "open":
            if self.clock() - self.opened_at < self.reset_timeout:
                return fallback()
            self.state = "half_open"
        try:
            result = fn()
        except Exception:
            self.recent.append(False)
            full = len(self.recent) == self.recent.maxlen
            if self.state == "half_open" or (full and self.recent.count(False) / len(self.recent) >= self.rate):
                self.state, self.opened_at = "open", self.clock()
            return fallback()
        self.recent.append(True)
        self.state = "closed"
        return result


if __name__ == "__main__":
    pattern = itertools.cycle([True, False])  # 성공·실패가 번갈아: 연속 3번 실패는 없지만 비율은 50%

    def flaky():
        if not next(pattern):
            raise TimeoutError
        return "ok"

    b = RateBreaker(rate=0.5, window=4, reset_timeout=60)
    print([b.call(flaky, lambda: "fallback") for _ in range(6)], b.state)
