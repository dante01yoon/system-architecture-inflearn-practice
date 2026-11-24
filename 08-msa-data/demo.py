"""주문·재고 두 서비스가 각자 sqlite 파일을 쓴다. 재고가 꺼졌을 때 동기 호출과 아웃박스 메시지를 비교한다."""
import sqlite3
from pathlib import Path

from order import OrderService
from stock import Down, StockService

DATA = Path(__file__).resolve().parent / "data"
ISBN = "9780134494166"  # Clean Architecture
clock = 0


def log(text):
    global clock
    print(f"   [t={clock}] {text}")  # t = 일이 일어난 순서
    clock += 1


def tables(path):
    rows = sqlite3.connect(path).execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY rowid")
    return ", ".join(r[0] for r in rows)


def main():
    DATA.mkdir(exist_ok=True)
    for f in DATA.glob("*.db"):
        f.unlink()
    stock, orders = StockService(DATA / "stock.db"), OrderService(DATA / "orders.db")
    with stock.db:
        stock.db.execute("INSERT INTO stock VALUES (?, 5)", (ISBN,))

    print("1) 서비스마다 자기 파일")
    print(f"   orders.db 테이블: {tables(DATA / 'orders.db')}")
    print(f"   stock.db  테이블: {tables(DATA / 'stock.db')}")

    print("2) 동기: 주문이 재고를 바로 부른다")
    log(f"주문 #{orders.place_sync(stock, ISBN, 2)} 2권 -> 확정 (재고 {stock.left(ISBN)}권)")
    stock.up = False
    log("재고 서비스 꺼짐")
    try:
        orders.place_sync(stock, ISBN, 1)
    except Down as e:
        failed = 1
        log(f"주문 1권 -> 실패: {e}")

    print("3) 비동기: 주문은 아웃박스에 쪽지만 남긴다")
    log(f"주문 #{orders.place_async(ISBN, 1)} 1권 -> 접수 (쪽지 {orders.waiting()}장 대기)")
    log(f"주문 #{orders.place_async(ISBN, 1)} 1권 -> 접수 (쪽지 {orders.waiting()}장 대기)")
    log(f"전달 시도 -> {orders.relay(stock)}장 전달, {orders.waiting()}장 남음")
    stock.up = True
    log("재고 서비스 다시 켜짐")
    log(f"전달 시도 -> {orders.relay(stock)}장 전달, 재고 {stock.left(ISBN)}권")
    done = orders.db.execute("SELECT COUNT(*) FROM orders WHERE status = '확정'").fetchone()[0]
    print(f"   확정 {done}건 · 실패 {failed}건(동기 때)")

    print("4) 동기 호출이 줄줄이 이어지면")
    for n in (1, 3, 5):
        print(f"   서비스 {n}개, 각 99% -> {0.99 ** n * 100:.1f}%")


if __name__ == "__main__":
    main()
