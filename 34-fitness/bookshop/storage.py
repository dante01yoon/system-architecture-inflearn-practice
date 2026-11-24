"""가장 아래 층: 책과 재고를 보관한다(사전 하나)."""


class Books:
    def __init__(self):
        self.stock = {"9780134494166": 3, "9781492097549": 5}
        self.price = {"9780134494166": 32000, "9781492097549": 45000}

    def take(self, isbn, qty):
        if qty > self.stock.get(isbn, 0):
            return False
        self.stock[isbn] -= qty
        return True
