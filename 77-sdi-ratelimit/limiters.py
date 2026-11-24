"""요청 수 제한 알고리즘 다섯 가지 (표준 라이브러리만). clock() = 지금 시각(초) — 테스트·데모는 가짜 시계를 넣는다."""
import math
import time
from collections import deque


class TokenBucket:
    """통에 토큰이 rate개/초로 차고(최대 capacity), 요청마다 1개를 꺼낸다."""
    def __init__(self, capacity, rate, clock=time.monotonic):
        self.capacity, self.rate, self.clock = capacity, rate, clock
        self.tokens, self.t = capacity, clock()

    def _refill(self):
        now = self.clock()
        self.tokens = min(self.capacity, self.tokens + (now - self.t) * self.rate)
        self.t = now

    def allow(self):
        self._refill()
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

    def retry_after(self):
        """토큰 1개가 찰 때까지 남은 초(Retry-After에 넣을 값, 올림)."""
        self._refill()
        return math.ceil(max(0.0, 1 - self.tokens) / self.rate)


class LeakyBucket:
    """물통(미터): 요청마다 물 1을 붓고, 물은 leak개/초로 샌다. 넘치면 거절."""
    def __init__(self, capacity, leak, clock=time.monotonic):
        self.capacity, self.leak, self.clock = capacity, leak, clock
        self.level, self.t = 0.0, clock()

    def allow(self):
        now = self.clock()
        self.level = max(0.0, self.level - (now - self.t) * self.leak)
        self.t = now
        if self.level + 1 <= self.capacity:
            self.level += 1
            return True
        return False


class FixedWindow:
    """window초마다 칸을 새로 열고, 칸 안에서 limit번까지."""
    def __init__(self, limit, window, clock=time.monotonic):
        self.limit, self.window, self.clock = limit, window, clock
        self.slot, self.count = None, 0

    def allow(self):
        slot = int(self.clock() // self.window)
        if slot != self.slot:
            self.slot, self.count = slot, 0
        if self.count < self.limit:
            self.count += 1
            return True
        return False


class SlidingLog:
    """통과한 요청 시각을 모두 적어 두고, 지난 window초 안의 개수만 센다."""
    def __init__(self, limit, window, clock=time.monotonic):
        self.limit, self.window, self.clock = limit, window, clock
        self.log = deque()

    def allow(self):
        now = self.clock()
        while self.log and self.log[0] <= now - self.window:
            self.log.popleft()
        if len(self.log) < self.limit:
            self.log.append(now)
            return True
        return False


class SlidingCounter:
    """칸 두 개(앞 칸 · 지금 칸)의 숫자만: 앞 칸 × 아직 겹친 비율 + 지금 칸."""
    def __init__(self, limit, window, clock=time.monotonic):
        self.limit, self.window, self.clock = limit, window, clock
        self.slot, self.prev, self.cur = None, 0, 0

    def allow(self):
        now = self.clock()
        slot = int(now // self.window)
        if slot != self.slot:
            self.prev = self.cur if self.slot == slot - 1 else 0
            self.slot, self.cur = slot, 0
        overlap = 1 - (now % self.window) / self.window
        if self.prev * overlap + self.cur < self.limit:
            self.cur += 1
            return True
        return False
