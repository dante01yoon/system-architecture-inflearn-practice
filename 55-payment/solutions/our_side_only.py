"""연습 문제 풀이: 거꾸로 맞춰 보기 — 우리는 CONFIRMED인데 PG 정산 보고서에는 결제가 없는 주문 찾기."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from orders import OrderService  # noqa: E402
from pg import FakePG  # noqa: E402


def our_side_only(svc):
    at_pg = {o for o, _, _ in svc.pg.settlement()}
    rows = svc.db.execute("SELECT id, state FROM orders WHERE state IN ('PAID', 'CONFIRMED')").fetchall()
    return [(o, s) for o, s in rows if o not in at_pg]   # 돈은 안 들어왔는데 표는 나감 → 사람이 확인


if __name__ == "__main__":
    pg = FakePG(); svc = OrderService(pg)
    svc.place(201, 18000); svc.checkout(201)
    svc.place(202, 18000); svc.paid(202, "버그: PG 확인 없이 확정")   # 일부러 만든 잘못
    print("PG에 없는 확정 주문:", our_side_only(svc))
