import unittest

from demo import REQUESTS, shop_log
from log import AuthorPopularity, DailySales, Search, Stock
from unique import partition, process, route


class PhiloTest(unittest.TestCase):
    def test_views_are_derived_and_rebuildable(self):
        log = shop_log()
        a = Stock().catch_up(log)
        log.append({"type": "BookSold", "book": "b1", "qty": 1, "price": 36000, "day": "11-14"})
        a.catch_up(log)
        self.assertEqual(a.count, Stock().catch_up(log).count)   # 버리고 처음부터 다시 만들어도 같다
        self.assertEqual(a.offset, len(log.events))

    def test_new_view_from_offset_zero_leaves_others_alone(self):
        log = shop_log()
        search, sales = Search().catch_up(log), DailySales().catch_up(log)
        before = (search.offset, dict(sales.won))
        pop = AuthorPopularity().catch_up(log)
        self.assertEqual(pop.sold, {"클레프만": 2, "파울러": 2})
        self.assertEqual((search.offset, sales.won), before)
        self.assertEqual(search.index["애플리케이션"], ["b1", "b4"])

    def test_username_unique_and_deterministic(self):
        out = [(r["request_id"], v) for part in route(REQUESTS) for r, v in process(part)]
        accepted = [rid for rid, v in out if v == "수락"]
        self.assertEqual(sorted(accepted), ["r1", "r2", "r4"])
        self.assertIn(("r3", "거절"), out)
        self.assertIn(("r2", "이미 처리됨"), out)
        self.assertEqual(out, [(r["request_id"], v) for part in route(REQUESTS) for r, v in process(part)])

    def test_same_username_same_partition(self):
        self.assertEqual(partition("minji"), partition("minji"))


if __name__ == "__main__":
    unittest.main()
