"""python3 demo.py 1 → 네트워크(요청이 사라졌나 응답이 사라졌나),  2 → 시계(LWW가 나중 쓰기를 버림),  3 → 멈춤과 펜싱 토큰"""
import sys

from clock import MonotonicClock, WallClock, lww_merge
from lock import LockService, Storage
from net import TIMEOUT, PaymentServer, call


def one():
    for i, (fate, what) in enumerate([("lost_request", "요청이 가다 사라짐"), ("lost_response", "응답이 오다 사라짐"), ("slow", "서버가 느림")], 1):
        s = PaymentServer()
        seen, ms = call(s, 36000, fate, seed=3)
        print(f"{i}. {what} → 손님이 본 것: {seen} {ms}ms, 실제 결제 {len(s.charges)}번")
    print(f"   손님 눈에는 셋이 똑같다: {TIMEOUT}ms 동안 답 없음")
    s = PaymentServer()
    call(s, 36000, "lost_response")
    call(s, 36000, "ok")
    print(f"4. 키 없이 다시 보내기 → 결제 {len(s.charges)}번, 합계 {sum(s.charges):,}원")
    s = PaymentServer()
    call(s, 36000, "lost_response", key="pay-7")
    call(s, 36000, "ok", key="pay-7")
    print(f"5. 멱등성 키 pay-7로 다시 → 결제 {len(s.charges)}번, 합계 {sum(s.charges):,}원")


def two():
    a, b = WallClock(skew=+500), WallClock(skew=-100)
    print("1. 노드 A 시계는 500ms 빠름, 노드 B 시계는 100ms 느림")
    w1 = {"value": "36,000원", "stamp": a.now(1000)}
    print(f"2. 실제 1000ms 관리자1이 A에 36,000원 → 도장 {w1['stamp']}")
    w2 = {"value": "32,400원", "stamp": b.now(1200)}
    print(f"3. 실제 1200ms 관리자2가 B에 32,400원 → 도장 {w2['stamp']}")
    print(f"4. LWW로 합치기 → {lww_merge([w1, w2])['value']} 남음")
    print("   나중에 쓴 32,400원이 오류 없이 사라짐")
    wall, mono = WallClock(), MonotonicClock()
    w0, m0 = wall.now(5000), mono.now(5000)
    wall.ntp_set(-800)                           # 재는 도중에 동기화가 벽시계를 되감음
    print("5. 200ms 걸리는 일을 재는 도중 NTP가 벽시계를 800ms 되감음")
    print(f"   벽시계로 잰 시간 {wall.now(5200) - w0}ms, 단조 시계로 잰 시간 {mono.now(5200) - m0}ms")


def scenario(fencing):
    lock, db = LockService(lease=10), Storage(fencing)
    t1 = lock.acquire("작업1", now=0)            # 작업1은 t=1초부터 15초 동안 멈춘다
    t2 = lock.acquire("작업2", now=10)           # 리스가 끝나서 작업2가 잠금을 얻는다
    ok2 = db.write("재고 4권", t2)
    ok1 = db.write("재고 9권", t1)               # 깨어난 작업1은 아직 잠금이 있다고 믿는다
    return t1, t2, ok2, ok1, db.value


def three():
    t1, t2, ok2, ok1, value = scenario(fencing=False)
    yes = {True: "받아들임", False: "거절"}
    print(f"1. t=0초 작업1이 잠금을 얻음 (리스 10초, 토큰 {t1})")
    print("2. t=1초 작업1이 멈춤: GC 15초")
    print(f"3. t=10초 리스 끝, 작업2가 잠금을 얻음 (토큰 {t2})")
    print(f"4. t=12초 작업2가 재고 4권 저장 → {yes[ok2]}")
    print(f"5. t=16초 작업1이 깨어나 재고 9권 저장 → {yes[ok1]}, 최종 {value}")
    print("   펜싱 없음: 잠금을 가진 작업이 둘, 작업2의 쓰기를 덮어씀")
    t1, t2, _, ok1, value = scenario(fencing=True)
    print(f"6. 펜싱 토큰 검사: {t1} < {t2} → {yes[ok1]}, 최종 {value}")


if __name__ == "__main__":
    {"1": one, "2": two, "3": three}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
