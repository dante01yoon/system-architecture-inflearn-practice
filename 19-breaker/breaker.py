"""Circuit Breaker: 실패가 threshold번 이어지면 열려서 바로 거절하고, reset_timeout이 지나면 한 번만 시험해 본다."""
import time


class CircuitBreaker:
    def __init__(self, threshold=3, reset_timeout=10, clock=time.monotonic):
        self.threshold, self.reset_timeout, self.clock = threshold, reset_timeout, clock
        self.state, self.failures, self.opened_at = "closed", 0, 0.0

    def call(self, fn, fallback):
        if self.state == "open":
            if self.clock() - self.opened_at < self.reset_timeout:
                return fallback()  # 부르지 않고 바로 대신할 답
            self.state = "half_open"  # 기다릴 만큼 기다렸다: 한 번만 시험
        try:
            result = fn()
        except Exception:
            self.failures += 1
            if self.state == "half_open" or self.failures >= self.threshold:
                self.state, self.opened_at = "open", self.clock()
            return fallback()
        self.state, self.failures = "closed", 0
        return result
