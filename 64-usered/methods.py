"""RED: 서비스마다 Rate·Errors·Duration / USE: 자원마다 Utilization·Saturation·Errors."""
import math


def p99(xs):
    s = sorted(xs)
    return s[max(0, math.ceil(len(s) * 0.99) - 1)]


def red(window):
    """엔드포인트마다 (초당 요청 수, 오류율 %, p99 걸린 시간 ms)."""
    by = {}
    for reqs, _ in window:
        for ep, sec, failed in reqs:
            by.setdefault(ep, []).append((sec, failed))
    out = {}
    for ep, rs in by.items():
        rate = len(rs) / len(window)
        errors = sum(f for _, f in rs) / len(rs) * 100
        duration = p99([s for s, _ in rs]) * 1000
        out[ep] = (rate, errors, duration)
    return out


def use(window):
    """자원마다 (평균 사용률 %, 평균 포화 = 줄 선 수, 오류 합계)."""
    out = {}
    for name in window[0][1]:
        u = sum(w[1][name][0] for w in window) / len(window)
        s = sum(w[1][name][1] for w in window) / len(window)
        e = sum(w[1][name][2] for w in window)
        out[name] = (u, s, e)
    return out


def suspicious(u, s, e):
    """Gregg의 기준: 사용률이 높거나(70% 이상), 줄이 있거나, 오류가 있으면 확인."""
    return u >= 70 or s > 0 or e > 0
