"""python3 demo.py 1 → 같은 장애를 세 방법으로,  python3 demo.py 2 → 경보에서 원인까지"""
import sys
import unicodedata

from incident import minutes
from methods import PAGE, burn, golden, red, use

LOG = minutes()


def pad(s, w):
    """한글은 두 칸으로 세어 왼쪽 정렬."""
    return s + " " * (w - sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s))


def one():
    print("1) 같은 장애 · 같은 숫자 (결제 API가 8분째부터 느려짐)")
    print("   분  SLO 소진    네 가지 신호   RED           USE")
    first = {}
    for t in range(6, 13):
        b, g, r, u = burn(LOG, t), golden(LOG[t], LOG[0]), red(LOG[t], LOG[0]), use(LOG[t])
        for k, v in {"SLO 호출": b >= PAGE, "네 신호": g, "RED": r, "USE": u}.items():
            if v:
                first.setdefault(k, t)
        rs = " ".join(f"{k} {'·'.join(v)}" for k, v in r.items()) or "-"
        us = " ".join(f"풀 {'·'.join(v)}" for k, v in u.items()) or "-"
        page = " 호출" if b >= PAGE else "     "
        print(f"  {t:2d}분 {b:5.1f}배{page} {pad('·'.join(g) or '-', 14)} {pad(rs, 13)} {us}")
    at = {}
    for k, t in first.items():
        at.setdefault(t, []).append(k)
    print("2) 처음 표시: " + " · ".join(f"{'·'.join(ks)} {t}분" for t, ks in sorted(at.items())))


def two(t=11):
    m = LOG[t]
    print(f"1) SLO · {t}분 /checkout 소진 속도 {burn(LOG, t):.1f}배 ≥ {PAGE}배 → 호출")
    print("2) RED · 어느 서비스가")
    for svc, (r, e, d) in m["svc"].items():
        print(f"   {svc:<10} {r:3d}/초 {e:5.1f}% {d:7,d}ms{'  ◀' if svc in red(m, LOG[0]) else ''}")
    print("3) USE · /checkout이 거치는 자원")
    for name, (u, s, e) in m["res"].items():
        print(f"   {pad(name, 11)} {u:4.0f}% {s:5.1f} {e:4d}{'  ◀' if name in use(m) else ''}")
    wait = m["res"]["DB 연결 풀"][1] / m["svc"]["/checkout"][0]   # 리틀의 법칙 W = L / λ
    print(f"4) 트레이스: 연결 대기 {wait * 1000:,.0f}ms · 결제 API 2,400ms · 쿼리 30ms")
    print("5) 원인: 결제 API를 기다리는 동안 DB 연결을 쥠")


if __name__ == "__main__":
    {"1": one, "2": two}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
