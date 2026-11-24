"""반짝 할인 모형: 주문이 몰릴 때 DB 앞에 줄(큐)을 두면? 시간은 실제로 흐르지 않고 계산만 한다."""
import heapq
import random
from collections import deque

N, SPAN = 2000, 10.0      # 10초 동안 주문 2,000건
WORKERS, SERVICE = 4, 0.04  # 일꾼 4명, 한 건 0.04초 → 합쳐서 초당 100건(= DB가 버티는 양)


def arrivals(seed=2026):
    rng = random.Random(seed)
    return sorted(rng.uniform(0, SPAN) for _ in range(N))


def simulate(limit, seed=2026):
    """limit = 줄에 설 수 있는 최대 건수(0이면 줄 없이 바로 DB, None이면 끝없이)."""
    free = [0.0] * WORKERS          # 일꾼마다 다음에 비는 시각
    waiting = deque()               # 줄에 선 주문이 일을 시작할 시각들(먼저 온 순서)
    done, rejected, waits, starts = 0, 0, [], []
    for t in arrivals(seed):
        while waiting and waiting[0] <= t:
            waiting.popleft()
        start = max(t, free[0])
        if start > t and limit is not None and len(waiting) >= limit:
            rejected += 1           # 빈 일꾼도 줄 자리도 없다 → 바로 거절
            continue
        heapq.heapreplace(free, start + SERVICE)
        if start > t:
            waiting.append(start)
        done += 1
        waits.append(start - t)
        starts.append((t, start))
    return {"done": done, "rejected": rejected, "max_wait": max(waits),
            "end": max(free), "starts": starts}


def queue_length(starts, t):
    """t초에 줄에 서 있는 주문 수: 이미 왔는데 아직 시작 못 한 것."""
    return sum(1 for a, s in starts if a <= t < s)
