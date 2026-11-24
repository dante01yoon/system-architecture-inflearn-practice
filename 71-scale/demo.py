"""서버 한 대에서 백만 명까지. 1 = 앞 네 단계, 2 = 뒤 네 단계."""
import sys

from sim import CORES, PAGES, PEAK, STEPS, WRITES, max_users


def show(first, last):
    print(f"가정: 한 명이 하루에 페이지 {PAGES}번 · 쓰기 {WRITES}번 · 최대 = 평균 × {PEAK}")
    print(f"      서버 한 대 = 코어 {CORES}개 (숫자는 모두 가정)")
    for i in range(first, last + 1):
        name, c = STEPS[i]
        users, neck, each = max_users(c)
        runner = min((k for k in each if k != neck), key=each.get)
        print(f"{i}) {'+ ' if i else ''}{name}")
        print(f"   최대 {users:,}명 · 막히는 곳: {neck} · 그다음: {runner} {each[runner]:,}명")
    if last == len(STEPS) - 1:
        print("다음 벽: 데이터 센터 한 곳이 멈추면 전부 멈춤 → 여러 지역")


if __name__ == "__main__":
    part = sys.argv[1] if len(sys.argv) > 1 else '1'
    show(*{'1': (0, 3), '2': (4, 7)}[part])
