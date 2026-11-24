"""리뷰 서비스가 12초 동안 멈췄을 때, 1초마다 오는 책 화면 요청 열여섯 번을 서킷 브레이커 없이 / 있게 보낸다."""
import sys

from breaker import CircuitBreaker
from review import Clock, ReviewService

FALLBACK = "리뷰를 잠시 불러올 수 없어요"


def run(use_breaker, show=()):
    clock = Clock()
    reviews = ReviewService(clock)
    breaker = CircuitBreaker(threshold=3, reset_timeout=4, clock=clock)
    waited = 0.0
    for t in range(16):
        clock.now = float(t)  # 손님은 1초마다 따로 온다(앞 손님이 기다리는 중이어도)
        reviews.down = t < 12  # 0~12초 동안 멈춰 있다가 되살아난다
        before, calls = breaker.state, reviews.calls
        if use_breaker:
            text = breaker.call(reviews.get, lambda: FALLBACK)
        else:
            try:
                text = reviews.get()
            except TimeoutError:
                text = FALLBACK
        waited += clock() - t
        if t in show:
            probe = before == "open" and reviews.calls > calls  # 열린 채로 불렀다 = 반쯤 열림에서 한 번 시험
            moved = f"{before} -> half_open -> {breaker.state}" if probe else (
                before if before == breaker.state else f"{before} -> {breaker.state}")
            print(f"   [t={t:2}s] {clock() - t:3.1f}초 · 실패 {breaker.failures} · {moved:<28} {text}")
    return waited, reviews.calls


def main(part=""):
    # 녹화 터미널은 19줄 — 1은 0~7초, 2는 8~15초와 2) 비교(인자 없으면 전부)
    if part != "2":
        print("1) 서킷 브레이커와 함께 (실패 3번이면 열림, 4초 뒤 한 번 시험)")
    with_b = run(True, show={"1": range(8), "2": range(8, 16)}.get(part, range(16)))
    if part == "1":
        return
    print("2) 비교: 손님이 기다린 시간 합계 / 리뷰 서비스를 부른 횟수")
    without = run(False)
    print(f"   브레이커 없이 {without[0]:4.1f}초 / {without[1]}번")
    print(f"   브레이커 있게 {with_b[0]:4.1f}초 / {with_b[1]}번")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
