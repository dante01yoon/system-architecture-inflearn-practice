"""python3 demo.py 1 → 초과 판매와 조건부 UPDATE,  2 → 대기실과 멱등성 키"""
import sys

from booking import (PEOPLE, SEATS, arrivals, atomic_reserve, connect, naive_read, naive_write, open_db,
                     peak_per_second, pct, run_threads, sold, waiting_room)

RATE = 100


def one():
    times = arrivals()
    peak = peak_per_second(times)
    print(f"1) {SEATS}석 · {PEOPLE:,}명 · 10초 (가정: 정각 직후가 가장 붐빔)")
    print(f"   가장 붐빈 1초: {peak:,}명 → 데이터베이스도 초당 {peak:,}번")
    print("2) 읽고 · 확인하고 · 쓰기 따로 · 스레드 3개")
    print("   가정: 읽고 쓰기까지 1ms, 그 사이 요청끼리는 서로 못 봄")
    path = open_db()
    run_threads(path, times, 1, naive_read, naive_write)
    n, left = sold(path)
    print(f"   예약 {n:,}건 · 남은 좌석 {left}  ← {n - SEATS:,}석 초과 판매")
    print("3) 조건부 UPDATE 한 문장 (left > 0 일 때만 하나 빼기)")
    path = open_db()
    run_threads(path, times, 1, None, lambda db, p, _: atomic_reserve(db, p))
    n, left = sold(path)
    print(f"   예약 {n:,}건 · 남은 좌석 {left} · 매진 응답 {PEOPLE - n:,}명")


def two():
    times = arrivals()
    (n, left), admitted, waits = waiting_room(times, RATE)
    print(f"1) 대기실 · 도착 순 번호표 · 1초에 {RATE}명씩 입장")
    print(f"   데이터베이스에 간 요청 {admitted:,}번 (대기실 없으면 {PEOPLE:,}번)")
    print(f"   초당 최대 {RATE}번 (없으면 {peak_per_second(times):,}번)")
    print(f"   예약 {n}건 · 남은 좌석 {left}")
    print(f"   좌석 받은 사람 대기 p50 {pct(waits, 50):.1f}초 · p99 {pct(waits, 99):.1f}초")
    print(f"   나머지 {PEOPLE - n:,}명은 {max(waits):.1f}초 뒤 매진 안내")
    print("2) 응답이 사라져 같은 멱등성 키로 다시 보냄")
    path = open_db(); db = connect(path)
    a = atomic_reserve(db, 1, key="k-7f3a")
    b = atomic_reserve(db, 1, key="k-7f3a")
    n, left = sold(path)
    print(f"   첫 요청 {'성공' if a else '실패'} · 다시 보냄 {'성공' if b else '실패'} · 예약 {n}건 · 남은 좌석 {left}")


if __name__ == "__main__":
    {"1": one, "2": two}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
