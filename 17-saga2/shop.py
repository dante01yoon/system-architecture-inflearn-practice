"""서비스 넷의 데이터와 로컬 트랜잭션. 두 방식이 똑같이 쓴다."""


class Shop:
    def __init__(self, stock=3, flaky=0):
        self.orders, self.paid, self.shipped = {}, {}, []
        self.stock = {"DDIA": stock}
        self.flaky = flaky                     # 배송이 앞으로 몇 번 잠깐 실패할지

    def create(self, o):  self.orders[o["id"]] = "PENDING"     # 아직 확정 전
    def approve(self, o): self.orders[o["id"]] = "APPROVED"
    def reject(self, o):  self.orders[o["id"]] = "REJECTED"    # 주문의 보상

    def charge(self, o):
        if o.get("card") == "거절":
            raise ValueError("카드 거절")
        self.paid[o["id"]] = "PAID"

    def refund(self, o):  self.paid[o["id"]] = "REFUNDED"      # 결제의 보상

    def reserve(self, o):
        if self.stock[o["book"]] < o["qty"]:
            raise ValueError("재고 부족")
        self.stock[o["book"]] -= o["qty"]

    def release(self, o): self.stock[o["book"]] += o["qty"]    # 재고의 보상

    def ship(self, o):
        if self.flaky:
            self.flaky -= 1
            raise TimeoutError("배송사 응답 없음")
        self.shipped.append(o["id"])
