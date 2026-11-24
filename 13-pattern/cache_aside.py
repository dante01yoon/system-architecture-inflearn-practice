"""Cache-Aside: 부르는 쪽이 캐시를 직접 챙긴다."""


class Shop:
    def __init__(self, remote, forget=False):
        self.remote, self.cache = remote, {}
        self.forget = forget  # 캐시 지우기를 깜빡한 코드 흉내

    def price(self, isbn):
        if isbn in self.cache:  # 캐시에 있으면 바로
            return self.cache[isbn]
        value = self.remote.get(isbn)  # 없으면 원격에서
        self.cache[isbn] = value  # 가져와 넣고 돌려준다
        return value

    def change_price(self, isbn, price):
        self.remote.set(isbn, price)  # 원본을 먼저 바꾸고
        if not self.forget:
            self.cache.pop(isbn, None)  # 그다음 캐시를 지운다
