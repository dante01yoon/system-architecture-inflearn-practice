"""python3 demo.py 1 → 갱신 손실(SQLite),  2 → write skew(스냅샷 격리 장난감 모델)"""
import os
import sys
import tempfile

from txn import Conflict, cashier_store, clerks, leave, on_duty, open_db, sell_atomic, sell_read_then_write, stock


def one():
    path = os.path.join(tempfile.mkdtemp(), "shop.db")
    open_db(path, 10)
    print("1) 점원 둘이 같은 책을 한 권씩 판다 · 재고 10권")
    for line in clerks(path, sell_read_then_write):
        print("   " + line)
    print(f"   결과: 두 권 팔렸는데 재고 {stock(path)}  ← 갱신 손실(lost update)")
    open_db(path, 10)
    print("2) 고침: UPDATE … SET stock = stock - 1 WHERE stock > 0")
    for line in clerks(path, sell_atomic):
        print("   " + line)
    print(f"   결과: 재고 {stock(path)}")
    open_db(path, 1)
    print("3) 마지막 한 권을 둘이 동시에 · 재고 1권")
    for line in clerks(path, sell_atomic):
        print("   " + line)
    print(f"   결과: 재고 {stock(path)}")


def run_both(lock_row):
    db = cashier_store()
    a, b = db.begin(), db.begin()            # 둘 다 같은 스냅샷에서 시작
    for name, tx in (("민지", a), ("준호", b)):
        print(f"   {name}: 근무 중 {leave(tx, name, lock_row)}명 → 나는 빠져도 됨")
    res = []
    for name, tx in (("민지", a), ("준호", b)):
        try:
            tx.commit(); res.append(f"{name} 커밋 OK")
        except Conflict:
            res.append(f"{name} 커밋 실패")
    print("   " + " · ".join(res))
    return on_duty(db.begin())


def two():
    print("1) 스냅샷 격리(장난감 모델) · 계산대 근무 2명")
    print(f"   결과: 근무 중 {run_both(False)}명  ← write skew")
    print("2) 고침 ① 둘 다 「교대표」 한 줄을 고치게")
    print(f"   결과: 근무 중 {run_both(True)}명")
    print("3) 고침 ② 한 번에 하나씩(직렬 실행)")
    db = cashier_store()
    for name in ("민지", "준호"):
        tx = db.begin(); n = leave(tx, name); tx.commit()
        print(f"   {name}: 근무 중 {n}명 → {'퇴근' if n >= 2 else '못 빠짐'}")
    print(f"   결과: 근무 중 {on_duty(db.begin())}명")


if __name__ == "__main__":
    {"1": one, "2": two}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
