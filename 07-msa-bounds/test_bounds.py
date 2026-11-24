import unittest

from catalog import SHELF
from ordering import MAX_ITEMS, Order, Rejected
from translate import add_to_order, to_parcels

CA, RI = "9780134494166", "9781680502398"


class BoundsTest(unittest.TestCase):
    def setUp(self):
        self.order = Order("T")
        add_to_order(self.order, SHELF[CA], 2)

    def test_outside_cannot_change_lines(self):
        with self.assertRaises(AttributeError):
            self.order.lines.append("x")
        with self.assertRaises(AttributeError):
            self.order.lines[0].qty = 99
        self.assertEqual(self.order.total(), 64000)

    def test_max_items_invariant(self):
        add_to_order(self.order, SHELF[RI], MAX_ITEMS - 2)
        with self.assertRaises(Rejected):
            add_to_order(self.order, SHELF[CA], 1)
        self.assertEqual(sum(x.qty for x in self.order.lines), MAX_ITEMS)

    def test_total_never_negative(self):
        with self.assertRaises(Rejected):
            self.order.discount(64001)
        self.order.discount(64000)
        self.assertEqual(self.order.total(), 0)

    def test_translation_keeps_only_what_shipping_needs(self):
        p = to_parcels(self.order)[0]
        self.assertEqual((p.isbn, p.weight_g, p.qty), (CA, 680, 2))
        self.assertFalse(hasattr(p, "title"))


if __name__ == "__main__":
    unittest.main()
