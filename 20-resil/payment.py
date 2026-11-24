"""결제 서버(sqlite3). 멱등성 키가 오면 첫 응답을 저장해 두고, 같은 키면 그 응답만."""
import json
import sqlite3


class PaymentServer:
    def __init__(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("CREATE TABLE charges (id INTEGER PRIMARY KEY, order_id, amount)")
        self.db.execute("CREATE TABLE idem (key PRIMARY KEY, request, response)")
        self.lose_reply = 0  # 앞으로 몇 번의 응답이 돌아오는 길에 사라질지

    def charge(self, order_id, amount, key=None):
        request = json.dumps([order_id, amount])
        with self.db:
            if key:
                row = self.db.execute("SELECT request, response FROM idem WHERE key = ?",
                                      (key,)).fetchone()
                if row and row[0] != request:
                    raise ValueError("같은 키에 다른 요청")
                if row:
                    return json.loads(row[1])  # 이미 한 결제: 다시 하지 않고 응답만
            cur = self.db.execute("INSERT INTO charges (order_id, amount) VALUES (?, ?)",
                                  (order_id, amount))
            response = {"charge": cur.lastrowid, "amount": amount}
            if key:
                self.db.execute("INSERT INTO idem VALUES (?, ?, ?)",
                                (key, request, json.dumps(response)))
        if self.lose_reply:
            self.lose_reply -= 1
            raise ConnectionError("응답이 오는 길에 끊김")  # 결제는 이미 됐다
        return response

    def total(self, order_id):
        return self.db.execute("SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM charges"
                               " WHERE order_id = ?", (order_id,)).fetchone()
