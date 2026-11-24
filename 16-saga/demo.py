"""긴 트랜잭션 하나 대 Saga: 잠금, 성공, 3단계 실패와 거꾸로 보상, 중간 상태가 보이는 것."""
import contextlib
import io
import sys
from pathlib import Path

import shop
from saga import Saga

DATA = Path(__file__).resolve().parent / "data"


def other_customer(n):                       # 다른 연결 = 다른 손님
    try:
        with shop.open_db(DATA / "shop.db") as b:
            shop.create_order(b, {"id": n, "book": "Refactoring", "qty": 1})
        return f"다른 손님 주문 #{n}: 접수"
    except Exception as e:
        return f"다른 손님 주문 #{n}: 막힘 ({e})"


def main(part=""):
    DATA.mkdir(exist_ok=True)
    (DATA / "shop.db").unlink(missing_ok=True)
    db = shop.open_db(DATA / "shop.db")
    with db:
        db.execute("INSERT INTO stock VALUES ('DDIA', 3), ('Refactoring', 9)")

    # 녹화 터미널은 19줄 — 1은 1)·2), 2는 3)만 보여 준다(인자 없으면 전부). 2도 1)·2)를 조용히 돌려 같은 재고에서 시작
    quiet = contextlib.redirect_stdout(io.StringIO()) if part == "2" else contextlib.nullcontext()
    with quiet:
        part12(db)
    if part == "1":
        return
    part3(db)


def part12(db):
    print("1) 긴 트랜잭션 하나: 주문 #1을 네 단계 끝까지 한 번에")
    db.execute("BEGIN IMMEDIATE")            # 끝날 때까지 쓰기 잠금을 쥔다
    for _, t, _ in shop.STEPS:
        t(db, {"id": 1, "book": "DDIA", "qty": 1, "price": 30})
    print(f"   그동안 {other_customer(101)}")
    db.commit()

    print("2) Saga 성공: 주문 #2, 단계마다 커밋")
    s = Saga(shop.STEPS)
    n = iter(range(102, 110))
    ok = s.run(db, {"id": 2, "book": "DDIA", "qty": 1, "price": 30}, watch=lambda: other_customer(next(n)))
    for line in s.timeline:
        print(f"   {line}")
    print(f"   결과: {'완료' if ok else '실패'}")



def part3(db):
    print("3) Saga 실패: 주문 #3, 3단계 재고에서 (DDIA 2권 주문)")
    s = Saga(shop.STEPS)
    view = shop.open_db(DATA / "shop.db")
    peek = lambda: "다른 손님이 본 주문 #3: %s · 결제 %s" % (
        view.execute("SELECT status FROM orders WHERE id = 3").fetchone()[0],
        (view.execute("SELECT status FROM payments WHERE order_id = 3").fetchone() or ["없음"])[0])
    ok = s.run(db, {"id": 3, "book": "DDIA", "qty": 2, "price": 60}, watch=peek)
    for line in s.timeline:
        print(f"   {line}")
    print(f"   결과: {'완료' if ok else '실패'} → {peek()}")
    left = db.execute("SELECT qty FROM stock WHERE book = 'DDIA'").fetchone()[0]
    print(f"   지워진 행 없음: 주문 {db.execute('SELECT COUNT(*) FROM orders').fetchone()[0]}건, 재고 DDIA {left}권")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
