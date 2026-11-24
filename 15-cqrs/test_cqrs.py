from bookshop.commands import OutOfStock, PlaceOrder, handle_place_order
from bookshop.projector import project
from bookshop.queries import get_my_orders
from bookshop.schema import READ_SCHEMA, WRITE_SCHEMA, open_db


def test_order_reaches_read_side_only_after_projection_and_rejects_overselling():
    w, r = open_db(":memory:", WRITE_SCHEMA), open_db(":memory:", READ_SCHEMA)
    w.execute("INSERT INTO books VALUES ('Release It!', 1)")
    handle_place_order(w, PlaceOrder("dante", {"Release It!": 1}))
    assert get_my_orders(r, "dante") == []
    assert project(w, r) == 1 and project(w, r) == 0
    assert get_my_orders(r, "dante") == [(1, "Release It! · 모두 1권")]
    try:
        handle_place_order(w, PlaceOrder("dante", {"Release It!": 1}))
        raise AssertionError("재고 초과 주문이 통과함")
    except OutOfStock:
        assert w.execute("SELECT COUNT(*) FROM orders").fetchone() == (1,)


if __name__ == "__main__":
    test_order_reaches_read_side_only_after_projection_and_rejects_overselling()
    print("ok")
