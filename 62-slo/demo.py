"""SLO 실행: 1 = 평범한 한 달, 2 = 17일 14:00 결제 장애 25분이 있는 한 달."""
import sys

from slo import DAYS, MIN, SLO, alerts, budget, burn, clock, month, sli

INCIDENT = (16 * MIN + 14 * 60, 25, 0.68)   # 17일 14:00부터 25분, 결제 요청 68% 실패(가정)


def report(rows):
    good, valid = sli(rows)
    allowed, used = budget(rows)
    print(f"1) 30일 결제 요청 {sum(t for t, _, _ in rows):,}건 · 4xx 빼고 유효 {valid:,}건")
    print(f"2) SLI = 좋은 요청 / 유효 요청 = {good:,} / {valid:,} = {good / valid:.3%}")
    print(f"3) SLO {SLO:.1%} → 에러 버짓 = 유효의 0.1% = {allowed:,.0f}건")
    print(f"   시간으로 치면 30일 × 0.1% = {DAYS * MIN * (1 - SLO):.1f}분")
    print(f"4) 쓴 예산 {used:,}건 = {used / allowed:.0%} · 남은 예산 {allowed - used:,.0f}건 ({(1 - used / allowed) * DAYS * MIN * (1 - SLO):.1f}분)")
    return used / allowed


def good_month():
    rows = month()
    report(rows)
    end = len(rows)
    print(f"5) 마지막 1시간 소진 속도 {burn(rows, end, 60):.1f}배 · 6시간 {burn(rows, end, 360):.1f}배")
    a = alerts(rows)
    print(f"6) 다중 창 경보: {len(a)}번 울림")
    print("   정책: 예산이 남았으니 새 기능 출시 계속")


def bad_month():
    rows = month(incident=INCIDENT)
    start, length, _ = INCIDENT
    inc = sum(s for _, _, s in rows[start:start + length])
    print(f"0) 장애: {clock(start)}부터 {length}분, 결제 요청 68% 실패")
    left = report(rows)
    allowed, _ = budget(rows)
    print(f"   그중 장애 25분이 {inc:,}건 = 예산의 {inc / allowed:.0%}")
    (on_t, _, why), (off_t, _, _) = alerts(rows)
    print(f"5) {clock(on_t)} 경보 울림 ({why})")
    m = start + 10
    print(f"6) {clock(m)} 소진 속도: 1시간 {burn(rows, m, 60):.1f}배 · 6시간 {burn(rows, m, 360):.1f}배")
    print(f"7) {clock(off_t)} 경보 꺼짐 (짧은 창이 내려감)")
    print("   정책: " + ("예산을 다 씀 → 새 기능 출시 멈춤" if left >= 1 else f"남은 예산 {1 - left:.0%} → 출시는 계속, 원인부터 고치기"))


if __name__ == "__main__":
    {"1": good_month, "2": bad_month}[(sys.argv[1:] or ["1"])[0]]()
