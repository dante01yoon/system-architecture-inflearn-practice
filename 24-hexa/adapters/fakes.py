"""테스트용 어댑터: 진짜 DB·카드사·메일 없이 같은 포트에 맞춘다."""


class InMemoryBooks:
    def __init__(self, *books):
        self.rows = {b.isbn: b for b in books}

    def get(self, isbn):
        return self.rows.get(isbn)

    def save(self, book):
        self.rows[book.isbn] = book


class FakePayment:
    def __init__(self, approve=True):
        self.approve, self.charged = approve, []

    def charge(self, card, amount):
        if self.approve:
            self.charged.append(amount)
        return self.approve


class ListNotifier:
    def __init__(self):
        self.sent = []

    def send(self, text):
        self.sent.append(text)
