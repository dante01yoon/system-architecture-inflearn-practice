"""연습 문제 풀이: 실패한 호출을 한 번 더 부르면 실패는 줄고, 그만큼 지연이 붙는다. 실행: python3 -m solutions.retry"""
import random

from sim import net_call


def run_retry(calls, n=10_000, seed=7):
    rng = random.Random(seed)
    total, fails = [], 0
    for _ in range(n):
        ms, ok_all = 0.0, True
        for _ in range(calls):
            m, ok = net_call(rng)
            if not ok:
                m2, ok = net_call(rng)
                m += m2
            ms += m
            ok_all &= ok
        total.append(ms)
        fails += not ok_all
    total.sort()
    return {"avg": sum(total) / n, "p99": total[int(n * 0.99) - 1], "fail": fails / n}


if __name__ == "__main__":
    print("마이크로서비스 5번 + 재시도 1번:", {k: round(v, 4) for k, v in run_retry(5).items()})
