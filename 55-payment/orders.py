"""우리 주문 서비스: 상태 기계 + 웹훅 · 폴링 · 대사 세 갈래 + 감사 로그(sqlite3)."""
import sqlite3

NEXT = {"PENDING": {"PAID", "FAILED"},
        "PAID": {"CONFIRMED", "REFUND_NEEDED"},
        "REFUND_NEEDED": {"REFUNDED"}}


class OrderService:
    def __init__(self, pg):
        self.pg, self.db = pg, sqlite3.connect(":memory:", isolation_level=None)
        self.db.executescript("""
            CREATE TABLE orders(id INTEGER PRIMARY KEY, amount INTEGER,
                                state TEXT, seat_ok INTEGER);
            CREATE TABLE seen_events(id TEXT PRIMARY KEY);
            CREATE TABLE audit(order_id INTEGER, src TEXT, dst TEXT, why TEXT);""")

    def state(self, order):
        return self.db.execute("SELECT state FROM orders WHERE id=?", (order,)).fetchone()[0]

    def move(self, order, src, dst, why):
        """src일 때만 dst로(조건부 UPDATE). 바꾸면 같은 트랜잭션에서 감사 로그 한 줄."""
        assert dst in NEXT.get(src, ()), f"{src} → {dst} 금지"
        with self.db:
            self.db.execute("BEGIN")
            cur = self.db.execute("UPDATE orders SET state=? WHERE id=? AND state=?",
                                  (dst, order, src))
            if not cur.rowcount:
                return False
            self.db.execute("INSERT INTO audit VALUES(?, ?, ?, ?)", (order, src, dst, why))
        return True

    def place(self, order, amount, seat_ok=True):
        self.db.execute("INSERT INTO orders VALUES(?, ?, 'PENDING', ?)",
                        (order, amount, int(seat_ok)))

    def paid(self, order, why):
        """PG 결제가 확인됨(어느 길로든). 좌석이 살아 있으면 확정, 아니면 환불 필요."""
        if not self.move(order, "PENDING", "PAID", why):
            return self.state(order)                  # 이미 처리됨 → 아무것도 안 함
        ok = self.db.execute("SELECT seat_ok FROM orders WHERE id=?", (order,)).fetchone()[0]
        if ok:
            self.move(order, "PAID", "CONFIRMED", "좌석 확정")
        else:
            self.move(order, "PAID", "REFUND_NEEDED", "좌석 만료")
        return self.state(order)

    def checkout(self, order, faults=()):
        amount = self.db.execute("SELECT amount FROM orders WHERE id=?", (order,)).fetchone()[0]
        try:
            self.pg.charge(f"pay-{order}", order, amount, faults)
        except TimeoutError:
            return self.state(order)                  # 결과를 모른다 → PENDING 그대로 둔다
        return self.paid(order, "PG 응답")

    def on_webhook(self, evt):
        """웹훅은 최소 한 번 온다 → 이벤트 ID를 먼저 적고, 처음 본 것만 처리."""
        cur = self.db.execute("INSERT OR IGNORE INTO seen_events VALUES(?)", (evt["id"],))
        if not cur.rowcount:
            return "중복 무시"
        if self.state(evt["order"]) != "PENDING":
            return "이미 처리됨"                      # PG 응답이 먼저 와서 끝난 주문
        return self.paid(evt["order"], "웹훅")

    def poll(self):
        """두 번째 길: PENDING 주문을 우리가 PG에 직접 물어본다."""
        for (order,) in self.db.execute("SELECT id FROM orders WHERE state='PENDING'").fetchall():
            try:
                if self.pg.lookup(f"pay-{order}") == "paid":
                    self.paid(order, "폴링")
            except TimeoutError:
                pass                                  # 다음 폴링이나 대사 작업이 다시 본다

    def mismatches(self):
        """대사: PG 정산 보고서와 우리 주문을 한 줄씩 맞춰 본다."""
        want = {"paid": "CONFIRMED", "refunded": "REFUNDED"}
        return [(o, s, self.state(o)) for o, _, s in self.pg.settlement()
                if self.state(o) != want[s]]

    def reconcile(self):
        fixed = []
        for order, pg_state, ours in self.mismatches():
            if pg_state == "paid" and ours == "PENDING":
                ours = self.paid(order, "대사")
            if ours == "REFUND_NEEDED":               # Saga의 보상: 돈을 돌려준다
                self.pg.refund(f"pay-{order}")
                self.move(order, "REFUND_NEEDED", "REFUNDED", "PG 환불")
            fixed.append((order, self.state(order)))
        return fixed

    def audit(self, order):
        return self.db.execute("SELECT src, dst, why FROM audit WHERE order_id=?",
                               (order,)).fetchall()
