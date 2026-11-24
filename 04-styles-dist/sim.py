"""요청 하나가 서비스 여러 개를 건널 때 늘어나는 네트워크 호출·지연·실패를 흉내 낸다(표준 라이브러리만)."""
import random

LOCAL_MS = 0.01  # 같은 프로세스 안 함수 호출 한 번
NET_MS = 1.0     # 네트워크 호출 한 번의 보통 지연
SLOW_MS = 50.0   # 가끔 섞이는 느린 호출(재전송, 멈춤 등)
SLOW_P = 0.01    # 느린 호출이 나올 확률: 100번에 1번
FAIL_P = 0.001   # 호출 한 번이 실패할 확률: 1000번에 1번


def net_call(rng):
    """네트워크 호출 한 번: (걸린 ms, 성공했나)."""
    ms = NET_MS + rng.expovariate(1 / 0.3)
    if rng.random() < SLOW_P:
        ms += SLOW_MS
    return ms, rng.random() >= FAIL_P


def request(rng, calls, parallel=False):
    """요청 하나: 서비스를 calls번 부른다(0이면 프로세스 안)."""
    if calls == 0:
        return LOCAL_MS * 5, True
    res = [net_call(rng) for _ in range(calls)]
    ms = max(m for m, _ in res) if parallel else sum(m for m, _ in res)
    return ms, all(ok for _, ok in res)


def run(calls, parallel=False, n=10_000, seed=7):
    """요청 n개를 흉내 내 평균·p99·실패율을 낸다(시드가 같으면 결과도 같다)."""
    rng = random.Random(seed)
    res = [request(rng, calls, parallel) for _ in range(n)]
    ms = sorted(m for m, _ in res)
    fail = sum(not ok for _, ok in res) / n
    return {"avg": sum(ms) / n, "p99": ms[int(n * 0.99) - 1], "fail": fail}
