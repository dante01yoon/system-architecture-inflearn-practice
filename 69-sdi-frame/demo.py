"""python3 demo.py 1 → 45분 시간표,  2 → 60분 시간표,  3 → 위시리스트 연습지 만들기"""
import sys
import unicodedata
from pathlib import Path

from frame import timeline, worksheet


def pad(s, w):
    return s + " " * (w - sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s))


def show(total):
    print(f"1) {total}분 면접 시간표")
    for name, a, b in timeline(total):
        print(f"   {a:02d}–{b:02d}분  {pad(name, 12)} {'█' * (b - a)} {b - a}분")
    big = {n: b - a for n, a, b in timeline(total)}
    print(f"2) 뒤 두 걸음 {big['큰 그림'] + big['깊게 파기']}분 · 앞 다섯 걸음 {sum(big[n] for n in ['기능 요구', '비기능 요구', '어림셈', '핵심 엔티티', 'API'])}분")


def sheet():
    path = Path("wishlist.md")
    path.write_text(worksheet("서점 위시리스트"), encoding="utf-8")
    lines = path.read_text(encoding="utf-8").split("\n")
    print(f"1) {path} 작성 · {len(lines)}줄")
    print("2) 앞부분")
    for ln in lines[:12]:
        print(f"   {ln}")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "1"
    {"1": lambda: show(45), "2": lambda: show(60), "3": sheet}[arg]()
