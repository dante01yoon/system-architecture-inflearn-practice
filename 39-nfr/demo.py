"""python3 demo.py 1 → 응답 시간 분포,  python3 demo.py 2 → 여러 백엔드를 부를 때의 꼬리"""
import sys

from latency import chance_slow, histogram, page_times, percentile, sample, summary


def one():
    ms = sample()
    print(f"1) 주문 API 응답 시간 {len(ms):,}개")
    for k, v in summary(ms).items():
        print(f"   {k:>5}  {v:7.1f}ms" if k != "평균" else f"    {k}  {v:7.1f}ms")
    print("2) 구간별 개수 (막대는 로그 눈금)")
    for name, c, bar in histogram(ms):
        print(f"   {name:>11} {c:5d} {bar}")
    slow = sum(m > 200 for m in ms)
    print(f"3) 200ms 넘은 요청 {slow}개 — 평균만 보면 안 보이는 손님들")


def two():
    p99 = percentile(sample(200_000, 1), 99)
    print(f"1) 백엔드 하나의 p99 = {p99:.0f}ms (100번에 1번은 이보다 늦음)")
    print("2) 페이지 하나가 백엔드 N개를 부르면, 페이지가 p99보다 늦을 확률")
    print("      N     계산     시뮬레이션")
    for n in (1, 10, 100):
        pages = page_times(n)
        sim = sum(t > p99 for t in pages) / len(pages)
        print(f"   {n:4d}   {chance_slow(n):6.1%}   {sim:6.1%}")
    pages = page_times(10)
    print(f"3) 백엔드 10개 페이지의 p50 = {percentile(pages, 50):.0f}ms, p99 = {percentile(pages, 99):.0f}ms")


if __name__ == "__main__":
    {"1": one, "2": two}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
