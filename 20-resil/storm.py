"""재시도 몰림: 손님 100명이 동시에 실패한 뒤 다시 시도한다. 서버는 0.5초에 30건까지."""
import heapq
import random
from collections import Counter

from retry import backoff

SLOT, CAPACITY = 0.5, 30


def simulate(jitter, clients=100, seed=7):
    rng = random.Random(seed) if jitter else None
    todo = [(backoff(0, rng=rng), 1, i) for i in range(clients)]  # (보낼 시각, 몇 번째, 손님)
    heapq.heapify(todo)
    load, calls, done_at = Counter(), 0, 0.0
    while todo:
        t, attempt, who = heapq.heappop(todo)
        slot = int(t // SLOT)
        load[slot] += 1
        calls += 1
        if load[slot] > CAPACITY:  # 넘친 요청은 실패하고 더 오래 기다렸다 다시
            heapq.heappush(todo, (t + backoff(attempt, rng=rng), attempt + 1, who))
        else:
            done_at = max(done_at, t)
    return max(load.values()), calls, done_at
