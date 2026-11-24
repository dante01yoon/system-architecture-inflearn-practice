"""python3 demo.py 1 → RED로 아픈 서비스 찾기,  python3 demo.py 2 → USE로 그 안의 자원 찾기"""
import sys
import unicodedata

from methods import red, suspicious, use
from metrics import POOL, seconds


def pad(s, w):
    """한글은 두 칸으로 세어 왼쪽 정렬."""
    return s + " " * (w - sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s))


def one():
    log = seconds()
    before, now = red(log[:300]), red(log[300:])
    print("1) RED · 엔드포인트마다 (앞 5분 → 최근 5분)")
    print("   엔드포인트   초당 요청      오류율          p99")
    for ep in before:
        (r0, e0, d0), (r1, e1, d1) = before[ep], now[ep]
        print(f"   {ep:<10} {r0:3.0f} → {r1:3.0f}   {e0:4.1f}% → {e1:4.1f}%   {d0:5,.0f} → {d1:5,.0f}ms")
    worst = max(now, key=lambda ep: now[ep][1])
    print(f"2) 아픈 곳: {worst} · 요청 수는 그대로, 오류와 지연만 오름")


def two():
    log = seconds()
    now = use(log[300:])
    print("1) USE · /checkout이 거치는 자원 (최근 5분)")
    print("   자원         사용률   포화(줄)   오류")
    for name, (u, s, e) in now.items():
        mark = "  ◀ 확인" if suspicious(u, s, e) else ""
        print(f"   {pad(name, 12)} {u:4.0f}%   {s:6.1f}   {e:5d}{mark}")
    found = [n for n, v in now.items() if suspicious(*v)]
    print(f"2) 범인: {', '.join(found)} · 앱 CPU는 {now['앱 CPU'][0]:.0f}%로 한가함")
    hold = [use(w)["DB 연결 풀"][0] / 100 * POOL / red(w)["/checkout"][0] for w in (log[:300], log[300:])]
    print(f"3) 리틀의 법칙 W = L / λ: 연결 하나를 {hold[0]:.1f}초 → {hold[1]:.1f}초 쥠")


if __name__ == "__main__":
    {"1": one, "2": two}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
