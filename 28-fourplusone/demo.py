"""서점 모델 하나를 네 뷰로 찍고(views), 「책 주문하기」 시나리오로 맞춰 본다(check)."""
import copy
import sys
import unicodedata

from bookshop import MODEL, ORDER_A_BOOK
from fourplusone import VIEWS, show, walk

NOTE = {"logical": "클래스", "process": "프로세스", "development": "모듈", "physical": "서버"}


def pad(s, n):
    return s + " " * (n - sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s))


def views():
    for n, view in enumerate(VIEWS, 1):
        print(f"{n}) {VIEWS[view]}: {NOTE[view]} {len(MODEL[view])}개")
        for line in show(MODEL, view):
            if " → " in line or ": " in line:   # 이어진 것이 있는 줄만(화면 한 장에 들어가게)
                print(f"   {line}")


def check():
    print("5) 시나리오 「책 주문하기」로 네 뷰 맞춰 보기")
    for (i, step, bad), s in zip(walk(MODEL, ORDER_A_BOOK), ORDER_A_BOOK):
        where = f"{s['logical']} · {s['process']} · {s['development']}"
        print(f"   {i}. {pad(step, 15)}{pad(where, 37)}{'✗' if bad else '✓'}")
        for b in bad:
            print(f"      → {b}")
    fixed = copy.deepcopy(MODEL)
    fixed["physical"]["app-1"].append("mailer")
    left = sum(len(bad) for _, _, bad in walk(fixed, ORDER_A_BOOK))
    print(f"6) mailer를 app-1에 올린 뒤 다시: 문제 {left}건")


if __name__ == "__main__":
    {"views": views, "check": check}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: (views(), check()))()
