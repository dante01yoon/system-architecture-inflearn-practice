"""주문 한 건이 쓰기 DB에서 읽기 DB로 건너가는 모습을 순서대로 본다."""

from bookshop.commands import OutOfStock, PlaceOrder, handle_place_order
from bookshop.projector import project
from bookshop.queries import get_my_orders
from bookshop.schema import READ_SCHEMA, WRITE_SCHEMA, open_db

BOOKS = [("Clean Architecture", 5), ("Release It!", 3), ("Building Microservices", 1)]


def show(read_db) -> None:
    rows = get_my_orders(read_db, "dante")
    if not rows:
        print("   (주문 없음)")
    for order_id, summary in rows:
        print(f"   #{order_id}  {summary}")


def main() -> None:
    write_db = open_db(":memory:", WRITE_SCHEMA)
    read_db = open_db(":memory:", READ_SCHEMA)
    write_db.executemany("INSERT INTO books VALUES (?, ?)", BOOKS)

    print("1) 커맨드: 주문 넣기 -> 쓰기 DB")
    handle_place_order(
        write_db, PlaceOrder("dante", {"Clean Architecture": 2, "Release It!": 1})
    )
    print("   주문 저장, 이벤트 1건 기록")

    print("2) 쿼리: 내 주문 목록 <- 읽기 DB")
    show(read_db)

    print("3) 프로젝터: 이벤트를 읽기 DB에 반영")
    print(f"   {project(write_db, read_db)}건 반영")

    print("4) 쿼리: 내 주문 목록 <- 읽기 DB")
    show(read_db)

    print("5) 커맨드: 재고보다 많이 주문")
    try:
        handle_place_order(write_db, PlaceOrder("dante", {"Building Microservices": 2}))
    except OutOfStock as e:
        print(f"   거절: {e}")


if __name__ == "__main__":
    main()
