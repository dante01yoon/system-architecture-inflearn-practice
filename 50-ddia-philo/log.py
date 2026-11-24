"""덧붙이기만 하는 로그 하나 = 원본. 뷰(재고·검색·매출)는 모두 이 로그를 읽어 만든 파생 데이터."""


class Log:
    def __init__(self):
        self.events = []                      # 지우지도 고치지도 않는다

    def append(self, event):
        self.events.append(event)
        return len(self.events) - 1           # 오프셋 = 줄 번호

    def read(self, offset):
        return self.events[offset:]           # offset부터 끝까지


class View:
    """소비자 하나. 어디까지 읽었는지(offset)를 스스로 기억한다."""

    def __init__(self):
        self.offset = 0

    def catch_up(self, log):
        for event in log.read(self.offset):
            self.apply(event)
            self.offset += 1
        return self

    def apply(self, event):
        raise NotImplementedError


class Stock(View):
    def __init__(self):
        super().__init__(); self.count = {}

    def apply(self, e):
        if e["type"] == "StockReceived":
            self.count[e["book"]] = self.count.get(e["book"], 0) + e["qty"]
        if e["type"] == "BookSold":
            self.count[e["book"]] -= e["qty"]


class Search(View):
    def __init__(self):
        super().__init__(); self.index = {}

    def apply(self, e):
        if e["type"] == "BookAdded":
            for word in e["title"].split():
                self.index.setdefault(word, []).append(e["book"])


class DailySales(View):
    def __init__(self):
        super().__init__(); self.won = {}

    def apply(self, e):
        if e["type"] == "BookSold":
            self.won[e["day"]] = self.won.get(e["day"], 0) + e["qty"] * e["price"]


class AuthorPopularity(View):
    """나중에 새로 만드는 뷰: 작가별로 팔린 권수."""

    def __init__(self):
        super().__init__(); self.author = {}; self.sold = {}

    def apply(self, e):
        if e["type"] == "BookAdded":
            self.author[e["book"]] = e["author"]
        if e["type"] == "BookSold":
            name = self.author[e["book"]]
            self.sold[name] = self.sold.get(name, 0) + e["qty"]
