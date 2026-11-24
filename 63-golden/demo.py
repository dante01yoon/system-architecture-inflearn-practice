"""python3 demo.py 1 → 네 가지 신호 대시보드,  python3 demo.py 2 → 실패 요청 지연을 따로 봐야 하는 이유"""
import sys
import unicodedata

from log import hour
from signals import pages, signals

LEVELS = " .:-=+*#%@"


def pad(s, w):
    """한글은 두 칸으로 세어 왼쪽 정렬."""
    return s + " " * (w - sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s))


def spark(vals):
    """2분을 한 칸으로, 낮으면 ' ' 높으면 '@'."""
    lo, hi = min(vals), max(vals)
    pair = [max(vals[i:i + 2]) for i in range(0, len(vals), 2)]
    return "".join(LEVELS[round((v - lo) / (hi - lo or 1) * 9)] for v in pair)


def one():
    log = hour()
    rows = [signals(r) for r in log]
    print(f"1) 서점 요청 로그 60분 · {sum(map(len, log)):,}건 · 1분씩 묶음")
    print("2) 대시보드  0분" + "-" * 23 + "59분")
    for name, key, unit in (("지연 p99", "p99_ok", "ms"), ("트래픽", "rps", "/초"), ("오류율", "err", "%"), ("포화", "sat", "%")):
        v = [r[key] for r in rows]
        print(f"   {pad(name, 9)}|{spark(v)}| {min(v):,.0f}~{max(v):,.0f}{unit}")
    print("3)  분   초당   오류율   성공 p99   DB 풀")
    for m in (20, 29, 33, 42, 50):
        r = rows[m]
        print(f"   {m:3d}  {r['rps']:4.0f}  {r['err']:6.1f}%  {r['p99_ok']:7,.0f}ms  {r['sat']:4.0f}%")
    print("4) 증상 알림(오류율 1% 넘게 2분 연속) → 사람을 깨움")
    for m in pages(rows):
        print(f"   {m}분 · 오류율 {rows[m]['err']:.1f}% · 원인 단서: DB 풀 {rows[m]['sat']:.0f}%")


def two():
    rows = [signals(r) for r in hour()]
    print("1) 응답 시간 평균, 섞어 볼 때와 나눠 볼 때")
    print("    분   전체 평균   성공만   실패만   오류율")
    for m in (20, 33, 42):
        r = rows[m]
        bad = f"{r['avg_bad']:5.0f}ms" if r["avg_bad"] else "    -  "
        print(f"   {m:3d}   {r['avg_all']:6.0f}ms  {r['avg_ok']:6.0f}ms  {bad}  {r['err']:5.1f}%")
    calm, cut = rows[20], rows[42]
    print(f"2) 42분 전체 평균 {cut['avg_all']:.0f}ms < 평소 {calm['avg_all']:.0f}ms → 더 빨라 보임")
    print(f"   빠른 500이 {cut['err']:.0f}%라서 평균을 끌어내림")
    print(f"3) 33분 실패 평균 {rows[33]['avg_bad']:.0f}ms: 느린 실패가 더 나쁨")
    print("   → 성공 지연과 실패 지연을 따로 그린다")


if __name__ == "__main__":
    {"1": one, "2": two}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
