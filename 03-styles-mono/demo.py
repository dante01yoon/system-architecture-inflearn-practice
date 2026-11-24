"""같은 서점 기능(책 목록, 주문 + 쿠폰)을 세 가지 모놀리식 스타일로 만들고 비교한다."""
import sys
from pathlib import Path

from layered import presentation
from microkernel import core
from modular import app

HERE = Path(__file__).parent
STYLES = [("레이어드", "layered"), ("모듈러 모놀리스", "modular"), ("마이크로커널", "microkernel")]
ORDER = {"title": "Clean Architecture", "qty": 2, "coupon": "WELCOME10"}
LAYER = {"presentation": "프레젠테이션", "business": "비즈니스", "persistence": "퍼시스턴스", "database": "데이터베이스"}


def pad(s, n):
    """한글은 두 칸으로 세어 줄을 맞춘다."""
    return s + " " * (n - sum(2 if ord(c) > 0x1100 else 1 for c in s))


def hops(call):
    """call을 실행하는 동안 레이어드의 어느 층을 지났는지, 비즈니스 층에서 몇 줄이 실행됐는지."""
    seen, lines = [], [0]

    def line(frame, event, arg):
        if event == "line":
            lines[0] += 1
        return line

    def watch(frame, event, arg):
        name = frame.f_globals.get("__name__", "")
        if event != "call" or not name.startswith("layered."):
            return None
        layer = LAYER[name.split(".")[1]]
        if layer not in seen:
            seen.append(layer)
        return line if layer == "비즈니스" else None

    sys.settrace(watch)
    try:
        call()
    finally:
        sys.settrace(None)
    return seen, lines[0]


def touched(style):
    """쿠폰 기능 때문에 손댄 파일 = '쿠폰' 코드가 들어 있는 파일."""
    files = sorted(p for p in (HERE / style).rglob("*.py") if p.stat().st_size)
    hit = [p for p in files if "coupon" in p.read_text(encoding="utf-8").lower()]
    return [str(p.relative_to(HERE / style)) for p in hit], len(files)


def main():
    core.load_plugins()
    print("1) 같은 주문: Clean Architecture 2권 + 쿠폰 WELCOME10")
    totals = [presentation.post_order(ORDER), app.post_order(ORDER), core.place_order(ORDER)]
    for (name, _), total in zip(STYLES, totals):
        print(f"   {pad(name, 18)}{total:,}원")

    print("2) 레이어드: 요청이 지나간 층")
    for name, call in [("책 목록", presentation.get_books), ("주문", lambda: presentation.post_order(ORDER))]:
        layers, n = hops(call)
        print(f"   {pad(name, 8)}{' -> '.join(layers)}  (비즈니스 층 {n}줄)")

    print("3) 쿠폰 기능을 넣느라 손댄 파일")
    for name, style in STYLES:
        hit, total = touched(style)
        print(f"   {pad(name, 18)}{len(hit)}/{total}개  {', '.join(hit)}")

    print("4) 마이크로커널: 쿠폰 플러그인을 빼고 다시 주문")
    core.RULES.clear()
    print(f"   {core.place_order(ORDER):,}원  (core.py는 그대로)")


if __name__ == "__main__":
    main()
