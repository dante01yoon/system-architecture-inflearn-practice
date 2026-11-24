"""풀이: 헤지 요청(hedged request). 백엔드 하나가 p95보다 늦으면 같은 요청을 다른 복제본에 한 번 더 보내고, 먼저 온 답을 쓴다."""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from latency import percentile, sample  # noqa: E402

pool = sample(200_000, 1)
rnd = random.Random(3)
p95 = percentile(pool, 95)


def call():
    first = rnd.choice(pool)
    if first <= p95:
        return first
    return min(first, p95 + rnd.choice(pool))  # p95에서 두 번째 요청 출발


def page(calls, hedge):
    return max((call() if hedge else rnd.choice(pool)) for _ in range(calls))


for hedge in (False, True):
    pages = [page(10, hedge) for _ in range(10_000)]
    print("헤지 요청" if hedge else "그냥 부르기", f"백엔드 10개 페이지 p99 = {percentile(pages, 99):.0f}ms")
