import unittest

from bookshop import (OrderService, mail_by_notification, notification, ship_by_notification,
                      ship_by_state, state_transfer)
from sourcing import EVENTS, replay


def shop():
    s = OrderService()
    s.place(1, "민지", {"DDIA": 2}, "서울")
    return s


class EventTest(unittest.TestCase):
    def test_notification_carries_only_id_and_consumers_call_back(self):
        s = shop()
        e = notification(s.orders[1])
        self.assertEqual(e, {"type": "OrderPlaced", "order_id": 1})
        ship_by_notification(e, s), mail_by_notification(e, s)
        self.assertEqual(s.calls, 2)

    def test_state_transfer_needs_no_call_and_keeps_copy(self):
        s, copy = shop(), {}
        self.assertEqual(ship_by_state(state_transfer(s.orders[1]), copy), "서울로 2권")
        self.assertEqual(s.calls, 0)
        self.assertEqual(copy, {1: {"address": "서울", "books": {"DDIA": 2}}})

    def test_state_transfer_survives_source_down(self):
        s = shop()
        e1, e2 = notification(s.orders[1]), state_transfer(s.orders[1])
        s.up = False
        with self.assertRaises(ConnectionError):
            ship_by_notification(e1, s)
        self.assertEqual(ship_by_state(e2, {}), "서울로 2권")

    def test_replay_rebuilds_state(self):
        self.assertEqual(replay(EVENTS), {"status": "paid", "paid": 96000,
                                          "books": {"Clean Architecture": 1, "DDIA": 2}})
        self.assertEqual(replay(EVENTS[:2])["status"], "placed")


if __name__ == "__main__":
    unittest.main()
