"""python3 demo.py 1 → DNS 계획 경쟁 상태(고치기 전 · 뒤),  2 → 복구 뒤 리스 몰림과 조절(고치기 전 · 뒤)"""
import sys

from dns import Enactor, Zone, plan
from storm import lease_storm

NAME = "dynamodb.us-east-1.amazonaws.com"


def race(safe):
    z = Zone()
    a, b, c = Enactor(z, safe), Enactor(z, safe), Enactor(z, safe)
    z.plans[2] = plan(2)                              # 계획기가 계획 2를 만든다
    ok = a.start(2)                                   # A는 계획 2로 시작했다가 오래 늦어진다
    for g in range(3, 9):
        z.plans[g] = plan(g)                          # 그사이 계획기는 새 계획 3~8을 만든다
    b.start(8); b.finish()                            # B는 최신 계획 8을 바로 적용
    late = a.finish()                                 # 늦게 끝난 A가 옛 계획 2를 쓴다
    b.cleanup()                                       # B가 오래된 계획을 정리
    c.start(9); z.plans[9] = plan(9)
    return ok, late, len(z.record), c.finish()


def one():
    ok, late, n, nxt = race(safe=False)
    print("[고치기 전] 적용기 A · B · C, 처음엔 계획 1 적용")
    print(f"1. A가 계획 2 확인 → 지금(1)보다 새것: {ok}, 적용 시작 (늦어짐)")
    print("2. 그사이 계획기가 계획 3~8을 만듦")
    print("3. B가 최신 계획 8 적용 → 주소 3개")
    print(f"4. 늦게 끝난 A가 계획 2를 씀 → {late}, 새 계획 8을 덮음")
    print("5. B의 정리: 6보다 오래된 계획 삭제 → 계획 2도 지움")
    print(f"6. {NAME} → 주소 {n}개 (빈 레코드)")
    print(f"7. C가 계획 9 적용 → {nxt}")
    ok, late, n, nxt = race(safe=True)
    print("[고친 뒤] 쓰는 순간 다시 비교 + 쓰고 있는 계획은 지우지 않기")
    print(f"8. A가 계획 2를 쓰려 함 → 2 ≤ 8, {late}")
    print(f"9. {NAME} → 주소 {n}개")
    print(f"10. C가 계획 9 적용 → {nxt}")


def two():
    print("서버 600대가 한꺼번에 리스 요청 · 관리자는 1틱에 50개 처리")
    print("4틱 넘게 답이 없으면 보낸 쪽은 포기하고 다시 보냄")
    log = lease_storm()
    print("[고치기 전] 오는 대로 줄에 넣기")
    for i, t in enumerate((5, 20, 60), 1):
        leased, q, wasted = log[t]
        print(f"{i}. {t}틱: 리스 {leased}대, 줄 {q}개, 헛일 {wasted}번")
    print("   리스는 250대에서 멈추고 줄만 길어짐: 혼잡 붕괴")
    log = lease_storm(limit=200)
    done = min(t for t, v in log.items() if v[0] == 600)
    print("[고친 뒤] 줄이 200개를 넘으면 새 요청을 받지 않음 (조절)")
    leased, q, wasted = log[5]
    print(f"4. 5틱: 리스 {leased}대, 줄 {q}개, 헛일 {wasted}번")
    print(f"5. {done}틱에 600대 모두 리스, 헛일 {log[done][2]}번")


if __name__ == "__main__":
    {"1": one, "2": two}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
