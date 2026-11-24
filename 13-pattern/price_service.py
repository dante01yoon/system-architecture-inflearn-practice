"""느린 원격 가격 서비스(흉내). 부를 때마다 200ms 걸린다고 치고, 부른 횟수만 센다."""
COST_MS = 200


class PriceService:
    def __init__(self, prices):
        self.prices = dict(prices)
        self.calls = 0

    def get(self, isbn):
        self.calls += 1
        return self.prices[isbn]

    def set(self, isbn, price):
        self.prices[isbn] = price
