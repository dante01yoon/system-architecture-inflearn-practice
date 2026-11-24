import copy
import unittest

from bookshop import MODEL, ORDER_A_BOOK
from fourplusone import show, walk


class FourPlusOneTest(unittest.TestCase):
    def test_bookshop_has_one_deliberate_gap(self):
        problems = [(i, bad) for i, _, bad in walk(MODEL, ORDER_A_BOOK) if bad]
        self.assertEqual(problems, [(4, ["mailer: 어느 서버에도 없음"])])

    def test_fixed_model_is_consistent(self):
        m = copy.deepcopy(MODEL)
        m["physical"]["app-1"].append("mailer")
        self.assertTrue(all(not bad for _, _, bad in walk(m, ORDER_A_BOOK)))

    def test_missing_element_in_a_view(self):
        m = copy.deepcopy(MODEL)
        del m["development"]["shop/payment"]
        self.assertEqual(walk(m, ORDER_A_BOOK)[2][2], ["shop/payment: 개발 뷰에 없음"])

    def test_show_physical(self):
        self.assertEqual(show(MODEL, "physical")[0], "web-1: web")


if __name__ == "__main__":
    unittest.main()
