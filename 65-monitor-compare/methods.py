"""같은 숫자를 세 방법으로 읽는다: 네 가지 신호 · RED · USE. 그리고 SLO 소진 속도."""
SLO = 99.9        # /checkout 가용성 목표 %
PAGE = 14.4       # 이 배수로 타면 사람을 부른다(SRE 실습서 경보 표 첫 줄)
SLOW_MS = 1000    # 이 서점이 정한 지연 기준


def jumped(now, before):
    """평소보다 절반 넘게 늘거나 줄었나(트래픽 기준)."""
    return abs(now - before) > before / 2


def golden(m, base, svc="/checkout"):
    """손님 쪽 서비스 하나의 네 가지 신호. 포화 = 그 서비스가 쓰는 가장 꽉 찬 자원."""
    r, e, d = m["svc"][svc]
    sat = max(u for u, _, _ in m["res"].values())
    hits = [("지연", d > SLOW_MS), ("트래픽", jumped(r, base["svc"][svc][0])),
            ("오류", e > 1), ("포화", sat >= 80)]
    return [name for name, hit in hits if hit]


def red(m, base):
    """서비스마다 R·E·D 중 기준을 넘은 글자."""
    out = {}
    for svc, (r, e, d) in m["svc"].items():
        f = "R" * jumped(r, base["svc"][svc][0]) + "E" * (e > 1) + "D" * (d > SLOW_MS)
        if f:
            out[svc] = f
    return out


def use(m):
    """자원마다 U·S·E 중 걸린 글자(Gregg의 기준)."""
    out = {}
    for name, (u, s, e) in m["res"].items():
        f = "U" * (u >= 70) + "S" * (s > 0) + "E" * (e > 0)
        if f:
            out[name] = f
    return out


def burn(log, t, svc="/checkout", window=5):
    """최근 window분 오류율 ÷ 예산(100 − SLO). 1배 = 창 끝에 예산을 딱 다 씀."""
    xs = [log[k]["svc"][svc][1] for k in range(max(0, t - window + 1), t + 1)]
    return sum(xs) / len(xs) / (100 - SLO)
