"""오케스트레이션: 주문 Saga가 단계 목록을 들고, 커맨드를 보내고 답을 받아 다음을 정한다."""

STEPS = [  # (단계, 커맨드, 보상 커맨드, 다시 시도)
    ("결제", "payment.charge", "payment.refund", False),
    ("재고", "stock.reserve", "stock.release", False),   # 피벗: 여기를 넘으면 끝까지 간다
    ("배송", "shipping.ship", None, True),               # 피벗 뒤: 될 때까지 다시
]


class OrderSaga:
    def __init__(self, bus, shop):
        self.bus, self.shop, self.log = bus, shop, []
        bus.subscribe("saga.reply", self.on_reply)

    def start(self, o):
        self.o, self.i = o, 0
        self.shop.create(o)                       # 주문 서비스 자기 일: PENDING
        self.send()

    def send(self):
        self.bus.publish(STEPS[self.i][1], self.o)

    def on_reply(self, r):
        name, _, _, retry = STEPS[self.i]
        if r["ok"]:
            self.log.append(f"{name} 완료")
            self.i += 1
            return self.send() if self.i < len(STEPS) else self.shop.approve(self.o)
        if retry:
            self.log.append(f"{name} 다시 시도 ({r['why']})")
            return self.send()
        self.log.append(f"{name} 실패 ({r['why']})")
        for k in reversed(range(self.i)):           # 끝낸 단계를 거꾸로 보상
            self.bus.publish(STEPS[k][2], self.o)
            self.log.append(f"{STEPS[k][0]} 보상")
        self.shop.reject(self.o)
        self.log.append("주문 거절")


class Participant:
    """커맨드를 받아 자기 로컬 트랜잭션을 하고 답만 보낸다. 다음 단계는 모른다."""

    def __init__(self, bus, shop):
        self.bus, self.shop = bus, shop
        for cmd, do in {"payment.charge": shop.charge, "stock.reserve": shop.reserve,
                        "shipping.ship": shop.ship}.items():
            bus.subscribe(cmd, lambda o, do=do: self.handle(do, o))
        bus.subscribe("payment.refund", shop.refund)
        bus.subscribe("stock.release", shop.release)

    def handle(self, do, o):
        try:
            do(o)
            self.bus.publish("saga.reply", {"ok": True})
        except Exception as e:
            self.bus.publish("saga.reply", {"ok": False, "why": str(e)})
