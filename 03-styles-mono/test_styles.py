import unittest

import demo
from layered import presentation
from microkernel import core
from modular import app


class StylesTest(unittest.TestCase):
    def setUp(self):
        core.load_plugins()
        self.rules = list(core.RULES)

    def tearDown(self):
        core.RULES[:] = self.rules

    def test_three_styles_charge_the_same(self):
        self.assertEqual({presentation.post_order(demo.ORDER), app.post_order(demo.ORDER), core.place_order(demo.ORDER)}, {57600})

    def test_book_list_passes_through_business_layer(self):
        layers, lines = demo.hops(presentation.get_books)
        self.assertEqual(layers, ["프레젠테이션", "비즈니스", "퍼시스턴스", "데이터베이스"])
        self.assertEqual(lines, 1)
        self.assertGreater(demo.hops(lambda: presentation.post_order(demo.ORDER))[1], 1)

    def test_coupon_spread(self):
        self.assertEqual([len(demo.touched(s)[0]) for _, s in demo.STYLES], [3, 2, 1])
        self.assertNotIn("core.py", demo.touched("microkernel")[0])

    def test_unplugging_coupon_keeps_core_working(self):
        core.RULES.clear()
        self.assertEqual(core.place_order(demo.ORDER), 64000)


if __name__ == "__main__":
    unittest.main()
