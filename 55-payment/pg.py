"""가짜 결제 대행사(PG). 고장 넣기: 결제 뒤 응답 끊김 · 웹훅 두 번 · 웹훅 유실 · 조회 멈춤."""


class FakePG:
    def __init__(self):
        self.charges = {}        # 멱등성 키 → {"order", "amount", "status"}
        self.outbox = []         # 보낼 웹훅
        self.lookup_down = False
        self.n = 0

    def _event(self, kind, key):
        self.n += 1
        order = self.charges[key]["order"]
        return {"id": f"evt_{self.n}", "type": kind, "key": key, "order": order}

    def charge(self, key, order, amount, faults=()):
        if key not in self.charges:   # 같은 키 = 결제 한 번
            self.charges[key] = {"order": order, "amount": amount, "status": "paid"}
            evt = self._event("charge.succeeded", key)
            if "lost_webhook" not in faults:
                self.outbox.append(evt)
                if "duplicate_webhook" in faults:
                    self.outbox.append(evt)           # 같은 이벤트가 한 번 더(최소 한 번 전달)
        if "timeout_after_charge" in faults:
            raise TimeoutError("결제는 됐는데 응답이 오다 끊김")
        return self.charges[key]["status"]

    def deliver(self, handler):
        """쌓인 웹훅을 우리 서버에 보낸다."""
        while self.outbox:
            handler(self.outbox.pop(0))

    def lookup(self, key):
        if self.lookup_down:
            raise TimeoutError("조회 API 응답 없음")
        c = self.charges.get(key)
        return c["status"] if c else None

    def refund(self, key):
        self.charges[key]["status"] = "refunded"      # 이미 환불됐으면 그대로(멱등)
        return "refunded"

    def settlement(self):
        """정산 보고서: 이 PG가 아는 결제 전부."""
        return [(c["order"], c["amount"], c["status"]) for c in self.charges.values()]
