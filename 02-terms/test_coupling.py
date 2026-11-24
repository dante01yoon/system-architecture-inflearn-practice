import sys
import unittest
from pathlib import Path

from coupling import dependents, imports

HERE = Path(__file__).parent


class CouplingTest(unittest.TestCase):
    def test_tight_has_more_arrows_and_payment_change_reaches_everyone(self):
        tight = imports(HERE / "shop_tight")
        self.assertEqual(sum(map(len, tight.values())), 7)
        self.assertEqual(dependents(tight, "payment"), ({"orders"}, {"orders", "email", "stock"}))

    def test_loose_payment_change_reaches_no_one_but_events_reaches_all(self):
        loose = imports(HERE / "shop_loose")
        self.assertEqual(sum(map(len, loose.values())), 4)
        self.assertEqual(dependents(loose, "payment"), (set(), set()))
        self.assertEqual(dependents(loose, "events")[0], {"orders", "payment", "stock", "email"})

    def test_both_shops_still_work(self):
        import shop_loose
        from shop_tight import email, orders, payment

        orders.place_order("dante", "Clean Architecture", 3, 30)
        shop_loose.orders.place_order("dante", "Clean Architecture", 3, 30)
        for mail, pay in ((email, payment), (shop_loose.email, shop_loose.payment)):
            self.assertEqual(pay.charged, [("dante", 90)])
            self.assertIn(("admin", "Clean Architecture 품절"), mail.outbox)

    def test_solution_cuts_arrows(self):
        fixed = imports(HERE / "solutions" / "shop_tight_fixed")
        self.assertLessEqual(sum(map(len, fixed.values())), 5)
        self.assertEqual(dependents(fixed, "payment")[1], {"orders"})


if __name__ == "__main__":
    sys.exit(unittest.main())
