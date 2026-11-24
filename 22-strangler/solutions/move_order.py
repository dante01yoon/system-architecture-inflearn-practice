"""연습 풀이: order(주문)를 새 서비스로 옮기기. 쓰기는 나란히 돌리면 재고가 두 번 빠지므로, 재고를 한 번 옮겨 놓고 넘긴다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import legacy  # noqa: E402
import newshop  # noqa: E402
from facade import Facade  # noqa: E402

STOCK = {}  # 새 서비스가 가진 재고(넘긴 뒤로는 이것만 원본)


def order(isbn, qty):
    if qty > STOCK[isbn]:
        return {"ok": False, "left": STOCK[isbn]}
    STOCK[isbn] -= qty
    return {"ok": True, "left": STOCK[isbn]}


newshop.order = order

if __name__ == "__main__":
    f = Facade({"catalog": "new", "reviews": "new", "order": "legacy"})
    isbn = next(iter(legacy.BOOKS))
    print("넘기기 전", f.handle("order", isbn, 1))
    STOCK.update({k: row[2] for k, row in legacy.BOOKS.items()})  # 한 번 옮기기
    f.routes["order"] = "new"
    print("넘긴 뒤 ", f.handle("order", isbn, 1))
    print("레거시에 남은 일:", [n for n, w in f.routes.items() if w == "legacy"])
