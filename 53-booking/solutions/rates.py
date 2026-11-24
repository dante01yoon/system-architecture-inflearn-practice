"""연습 문제 풀이: 대기실 입장 속도를 바꾸면 기다림과 데이터베이스 부하가 어떻게 바뀌나. python3 solutions/rates.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import booking as b  # noqa: E402

times = b.arrivals()
print("초당 입장 · 데이터베이스 초당 최대 · 대기 p99")
for rate in (50, 100, 200, 400, 1000):
    (n, _), admitted, waits = b.waiting_room(times, rate)
    print(f"{rate:>8} · {rate:>18} · {b.pct(waits, 99):.2f}초  (예약 {n})")
