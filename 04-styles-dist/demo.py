"""스타일마다 요청 하나가 건너는 네트워크 호출 수를 바꿔 가며 지연과 실패를 비교한다."""
from sim import FAIL_P, SLOW_P, run

ROWS = [("모놀리스", 0, False), ("서비스 기반", 2, False), ("마이크로서비스", 5, False),
        ("마이크로서비스 동시", 5, True), ("마이크로서비스 사슬", 10, False)]


def pad(s, n):
    return s + " " * (n - sum(2 if ord(c) > 0x1100 else 1 for c in s))


def main():
    print("1) 가정: 네트워크 호출 한 번 = 보통 1ms 남짓")
    print("   100번에 1번은 50ms 더 느리고, 1000번에 1번은 실패")
    print("2) 요청 1만 개 (시드 7)")
    print(f"   {pad('스타일', 22)}{pad('호출', 6)}{pad('평균ms', 10)}{pad('p99ms', 10)}실패")
    for name, calls, par in ROWS:
        r = run(calls, par)
        print(f"   {pad(name, 22)}{calls:<6}{r['avg']:<10.2f}{r['p99']:<10.2f}{r['fail']:.2%}")
    print("3) 계산으로 본 확률 (호출 N번)")
    for n in (2, 5, 10):
        print(f"   N={n:<3} 느린 호출을 한 번 이상 만남 {1 - (1 - SLOW_P) ** n:.1%}   실패 {1 - (1 - FAIL_P) ** n:.2%}")


if __name__ == "__main__":
    main()
