import importlib
import unittest

import broker
import mediator
import shop


def fresh():
    importlib.reload(shop)
    b = broker.Broker()
    b.subscribe("order.placed", shop.stock_service)
    b.subscribe("stock.reserved", shop.payment_service)
    b.subscribe("payment.done", shop.mail_service)
    b.subscribe("payment.done", shop.report_service)
    return b


class TopoTest(unittest.TestCase):
    def test_pubsub_gives_each_subscriber_a_copy(self):
        b = fresh()
        b.publish("order.placed", {"id": 1, "book": "DDIA", "qty": 2})
        self.assertEqual(b.trace[-2:], ["payment.done -> mail_service", "payment.done -> report_service"])
        self.assertEqual((shop.stock["DDIA"], shop.paid, shop.sent), (3, [1], [1]))

    def test_poison_message_lands_in_dlq_after_three_tries_and_others_continue(self):
        b, calls = fresh(), []
        b.subscribe("order.placed", lambda m, br: calls.append(m["id"]))
        b.publish("order.placed", {"id": 4, "book": "DDIA", "qty": "두 권"})
        b.publish("order.placed", {"id": 5, "book": "Refactoring", "qty": 1})
        self.assertEqual([(t, h, m["id"]) for t, h, m in b.dead], [("order.placed", "stock_service", 4)])
        self.assertEqual(shop.paid, [5])
        self.assertEqual(calls, [4, 5])  # 다른 구독자는 독 메시지와 상관없이 받는다

    def test_handler_retried_exactly_max_tries(self):
        b, tries = broker.Broker(), []
        b.subscribe("t", lambda m, br: tries.append(1) or 1 / 0)
        b.publish("t", {"id": 9})
        self.assertEqual(len(tries), broker.MAX_TRIES)

    def test_mediator_undoes_done_steps_on_failure(self):
        fresh()
        m = mediator.Mediator([("재고", shop.reserve, shop.restock), ("결제", shop.charge, shop.nothing)])
        self.assertTrue(m.run({"id": 3, "book": "DDIA", "qty": 1, "card": "거절"}).startswith("실패: 결제"))
        self.assertEqual(shop.stock["DDIA"], 5)
        self.assertEqual(m.log, ["#3 재고", "#3 결제"])

    def test_broker_keeps_reserved_stock_when_payment_fails(self):
        b = fresh()
        b.publish("order.placed", {"id": 3, "book": "DDIA", "qty": 1, "card": "거절"})
        self.assertEqual(shop.stock["DDIA"], 4)


if __name__ == "__main__":
    unittest.main()
