"""python3 demo.py 1 → 롤링 카나리와 자동 되돌림,  python3 demo.py 2 → price를 price_krw로 무중단 이름 바꾸기"""
import sys
import unicodedata

from canary import BUDGET_30D, big_bang, rollout
from migrate import run, shop, work


def pad(s, w):
    return s + " " * (w - sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s))


def table(title, rows):
    print(title)
    print("   v2 몫   요청   오류   v1 오류율   소진 속도   판정")
    for share, n, bad, old, speed, verdict in rows:
        print(f"   {share:4d}%  {n:5d}  {bad:5d}      {old:4.2f}%   {speed:6.1f}배   {verdict}")


def one():
    table("1) v2 정상판 · 단계마다 10분 지켜보기", rollout(v2_fail=0.0003))
    rows = rollout(v2_fail=0.20)
    table("2) v2 버그판 · 결제 다섯 건 중 한 건 실패", rows)
    canary = sum(r[2] for r in rows)
    print(f"3) 손님이 본 오류: 카나리 {canary}건 · 한 번에 100%였다면 {big_bang(0.20)}건")
    print(f"   전체 요청의 {canary / 1000:.1%} · 30일 예산 {BUDGET_30D:,}건 중 {canary / BUDGET_30D:.1%} 대 {big_bang(0.20) / BUDGET_30D:.1%}")


def two():
    db, truth = shop()
    try:
        db.execute("ALTER TABLE books RENAME COLUMN price TO price_krw")
        errs = sum(work(db, truth, "v1", k)[0] for k in range(50))
        print(f"0) 바로 RENAME → v1 오류 {errs}건 (no such column: price)")
    finally:
        db.close()
    db, truth = shop()
    total = 0
    for i, (name, apps, errs, bad) in enumerate(run(db, truth), 1):
        total += errs + bad
        print(f"{i}) {pad(name, 15)} 앱 {pad(' + '.join(apps), 8)} 오류 {errs} · 어긋남 {bad}")
    print(f"7) 여섯 단계 동안 오류·어긋남 합계 {total}건")
    errs = sum(work(db, truth, "v3", k)[0] for k in range(50))
    print(f"8) 이제 v3로 되돌리면 → 오류 {errs}건 · 그래서 앞으로 고치기")


if __name__ == "__main__":
    {"1": one, "2": two}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
