"""응답 시간을 분포로 보기: 평균·중앙값·백분위, 그리고 여러 백엔드를 부를 때 꼬리가 커지는 현상."""
import math
import random


def sample(n=10_000, seed=42):
    """주문 API 응답 시간(밀리초) n개. 대부분 40ms 언저리, 가끔(1%) 디스크·GC 멈춤에 걸려 크게 늦는다."""
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        ms = rnd.lognormvariate(math.log(40), 0.4)
        if rnd.random() < 0.01:
            ms += rnd.uniform(300, 1200)
        out.append(ms)
    return out


def percentile(ms, p):
    """p번째 백분위(nearest-rank): 정렬했을 때 p%가 이 값 이하."""
    s = sorted(ms)
    return s[max(0, math.ceil(len(s) * p / 100) - 1)]


def summary(ms):
    return {"평균": sum(ms) / len(ms), "p50": percentile(ms, 50), "p95": percentile(ms, 95),
            "p99": percentile(ms, 99), "p99.9": percentile(ms, 99.9)}


EDGES = [25, 50, 100, 200, 500, 1000, math.inf]


def histogram(ms, width=30):
    """구간별 개수와 막대. 긴 꼬리도 보이게 막대 길이는 로그 눈금."""
    counts = [0] * len(EDGES)
    for m in ms:
        counts[next(i for i, e in enumerate(EDGES) if m < e)] += 1
    top = math.log10(max(counts) + 1)
    rows, lo = [], 0
    for e, c in zip(EDGES, counts):
        name = f"{lo}~{e}ms" if e != math.inf else f"{lo}ms~"
        rows.append((name, c, "#" * round(width * math.log10(c + 1) / top)))
        lo = e
    return rows


def page_times(calls, n=10_000, seed=1):
    """한 페이지가 백엔드 calls개를 동시에 부르면, 페이지는 가장 늦은 응답을 기다린다."""
    pool = sample(200_000, seed)
    rnd = random.Random(seed + 1)
    return [max(rnd.choice(pool) for _ in range(calls)) for _ in range(n)]


def chance_slow(calls, p=0.99):
    """백엔드 하나가 p 확률로 빠를 때, calls개 중 하나라도 느릴 확률."""
    return 1 - p ** calls
