"""분마다 네 가지 신호(지연·트래픽·오류·포화)를 계산한다."""
import math

POOL = 16          # DB 연결 풀 크기
SLOW_MS = 1000     # 약속: 1초 넘으면 오류로 친다(정책)


def p99(ms):
    s = sorted(ms)
    return s[max(0, math.ceil(len(s) * 0.99) - 1)] if s else 0.0


def signals(reqs):
    ok = [ms for ms, code, _ in reqs if code < 500]
    bad = [ms for ms, code, _ in reqs if code >= 500]
    explicit = len(bad)                                      # 500 응답
    implicit = sum(1 for _, c, good in reqs if c < 500 and not good)
    policy = sum(1 for ms, c, good in reqs if c < 500 and good and ms > SLOW_MS)
    rps = len(reqs) / 60
    in_use = rps * sum(ms for ms, *_ in reqs) / len(reqs) / 1000   # L = λW
    return {
        "rps": rps,
        "err": (explicit + implicit + policy) / len(reqs) * 100,
        "p99_ok": p99(ok), "p99_bad": p99(bad),
        "avg_all": sum(ms for ms, *_ in reqs) / len(reqs),
        "avg_ok": sum(ok) / len(ok),
        "avg_bad": sum(bad) / len(bad) if bad else None,
        "sat": min(in_use / POOL, 1) * 100,
    }


def pages(rows, limit=1.0, need=2):
    """증상 알림: 오류율이 limit%를 need분 연속 넘으면 사람을 깨운다."""
    out, run = [], 0
    for m, r in enumerate(rows):
        run = run + 1 if r["err"] > limit else 0
        if run == need:
            out.append(m)
    return out
