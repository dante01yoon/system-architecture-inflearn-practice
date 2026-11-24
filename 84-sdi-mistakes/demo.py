"""python3 demo.py 1 → 약한 판 대본 검사,  2 → 고친 판 대본 검사"""
import sys
import unicodedata
from pathlib import Path

from checker import RULES, check, flags


def pad(s, w):
    return s + " " * (w - sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s))


def show(name):
    r = check(Path("transcripts", name).read_text(encoding="utf-8"))
    print(f"{name} · 45분 연습 대본")
    print("1) 걸음별 시간")
    for step, m in r["phases"].items():
        print(f"   {pad(step, 10)} {'█' * max(1, m // 2)} {m}분")
    print("2) 신호")
    for key, ok, fix in RULES:
        unit = "분" if key == "말 없는 틈" else "번"
        print(f"   {pad(key, 12)} {r[key]:>2}{unit}  {'통과' if ok(r[key]) else '✗ ' + fix}")
    deep = r["phases"].get("깊게 파기", 0)
    print(f"3) 깊게 파기 {deep}분 {'통과' if deep >= 10 else '✗'} · 고칠 것 {len(flags(r))}개")


if __name__ == "__main__":
    show({"1": "weak.txt", "2": "better.txt"}[sys.argv[1] if len(sys.argv) > 1 else "1"])
