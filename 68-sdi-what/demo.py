"""python3 demo.py 1 → 약한 연습 판 채점,  python3 demo.py 2 → 강한 연습 판 채점"""
import sys
import unicodedata

from rubric import parse, score, weakest
from sessions import STRONG, WEAK


def pad(s, w):
    """한글은 두 칸으로 세어 왼쪽 정렬."""
    return s + " " * (w - sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s))


def report(title, text):
    rows = score(parse(text))
    print(f"1) {title}")
    for name, got, full, tip in rows:
        bar = "■" * got + "□" * (full - got)
        print(f"   {pad(name, 10)} {bar}  {got}/{full}")
    total = sum(r[1] for r in rows)
    print(f"2) 합계 {total}/{sum(r[2] for r in rows)} · 가장 약한 곳: {weakest(rows)}")
    print("3) 다음 연습에서 고칠 것")
    for name, got, full, tip in rows:
        if tip:
            print(f"   - {pad(name, 10)} {tip}")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "1"
    if arg == "1":
        report("약한 판 · URL 단축기 45분", WEAK)
    else:
        report("강한 판 · URL 단축기 45분", STRONG)
