"""python3 demo.py 1 → 고장 세 가지와 멈춘 주문,  2 → 대사 작업이 찾아서 고치기"""
import sys

from orders import OrderService
from pg import FakePG

KO = {"paid": "결제됨", "refunded": "환불됨"}


def shop(cases):
    pg = FakePG()
    svc = OrderService(pg)
    for order, faults, seat_ok in cases:
        svc.place(order, 18000, seat_ok)
        svc.checkout(order, faults)
        pg.deliver(svc.on_webhook)
    return pg, svc


def one():
    pg = FakePG()
    svc = OrderService(pg)
    cases = [(101, (), "정상"), (102, ("timeout_after_charge",), "결제 뒤 응답 끊김"),
             (103, ("duplicate_webhook",), "웹훅이 두 번"), (104, ("timeout_after_charge", "lost_webhook"), "응답 끊김 + 웹훅 유실")]
    print("사인회 좌석 주문 4건 · 18,000원씩")
    for i, (order, faults, what) in enumerate(cases, 1):
        svc.place(order, 18000)
        right_after = svc.checkout(order, faults)
        got = []
        pg.deliver(lambda e: got.append(svc.on_webhook(e)))
        print(f"{i}. {order} {what}")
        print(f"   결제 직후 {right_after} · 웹훅 {len(got)}번 {' / '.join(got) or '안 옴'}")
    print("5. 지금 상태 (PG ↔ 우리)")
    for o, _, s in pg.settlement():
        print(f"   {o}  PG {KO[s]}  ↔  {svc.state(o)}" + ("  ← 돈은 나갔는데 멈춤" if svc.state(o) == "PENDING" else ""))
    svc.poll()
    print(f"6. 우리가 PG에 물어보기(폴링) → 104 {svc.state(104)}")
    print(f"   103 상태 변경 {len(svc.audit(103))}번 · PG 결제 {len(pg.charges)}건")


def two():
    pg, svc = shop([(101, (), True), (104, ("timeout_after_charge", "lost_webhook"), True),
                    (105, ("timeout_after_charge", "lost_webhook"), False)])
    pg.lookup_down = True
    svc.poll()
    print("1. 폴링 → PG 조회 API도 응답 없음 · 104 · 105 그대로 PENDING")
    bad = svc.mismatches()
    print(f"2. 대사 작업: PG 정산 {len(pg.settlement())}건 ↔ 우리 주문 → 불일치 {len(bad)}건")
    for o, p, s in bad:
        print(f"   {o}  PG {KO[p]}  ↔  {s}")
    for i, (o, s) in enumerate(svc.reconcile(), 3):
        print(f"{i}. {o} 고침 → {s}")
    print(f"5. 다시 대사 → 불일치 {len(svc.mismatches())}건")
    print("6. 105 감사 로그")
    for src, dst, why in svc.audit(105):
        print(f"   {src} → {dst}  ({why})")


if __name__ == "__main__":
    {"1": one, "2": two}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
