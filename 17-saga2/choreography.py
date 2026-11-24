"""코레오그래피: 지휘자 없음. 서비스마다 남의 이벤트를 구독하고, 일을 마치면 자기 이벤트를 올린다."""


class OrderService:
    def __init__(self, bus, shop):
        self.bus, self.shop = bus, shop
        bus.subscribe("Shipped", self.on_shipped)
        bus.subscribe("PaymentFailed", self.on_failed)
        bus.subscribe("StockFailed", self.on_failed)

    def place(self, o):
        self.shop.create(o)
        self.bus.publish("OrderCreated", o)

    def on_shipped(self, o): self.shop.approve(o)
    def on_failed(self, o):  self.shop.reject(o)


class PaymentService:
    def __init__(self, bus, shop):
        self.bus, self.shop = bus, shop
        bus.subscribe("OrderCreated", self.on_created)
        bus.subscribe("StockFailed", self.on_stock_failed)

    def on_created(self, o):
        try:
            self.shop.charge(o)
        except ValueError:
            return self.bus.publish("PaymentFailed", o)
        self.bus.publish("PaymentDone", o)

    def on_stock_failed(self, o): self.shop.refund(o)


class StockService:
    def __init__(self, bus, shop):
        self.bus, self.shop = bus, shop
        bus.subscribe("PaymentDone", self.on_paid)

    def on_paid(self, o):
        try:
            self.shop.reserve(o)
        except ValueError:
            return self.bus.publish("StockFailed", o)
        self.bus.publish("StockReserved", o)


class ShippingService:
    def __init__(self, bus, shop):
        self.bus, self.shop = bus, shop
        bus.subscribe("StockReserved", self.on_reserved)

    def on_reserved(self, o):
        self.shop.ship(o)
        self.bus.publish("Shipped", o)


def wire(bus, shop):
    order = OrderService(bus, shop)
    PaymentService(bus, shop), StockService(bus, shop), ShippingService(bus, shop)
    return order
