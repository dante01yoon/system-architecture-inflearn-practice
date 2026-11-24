import unittest

import legacy
import newshop
from facade import Facade


class StranglerTest(unittest.TestCase):
    def test_new_service_answers_like_legacy(self):
        for isbn in legacy.BOOKS:
            self.assertEqual(newshop.catalog(isbn), legacy.catalog(isbn))
            self.assertEqual(newshop.reviews(isbn), legacy.reviews(isbn))

    def test_route_table_decides_who_answers(self):
        f = Facade({"catalog": "legacy", "reviews": "new"})
        isbn = next(iter(legacy.BOOKS))
        self.assertEqual(f.handle("catalog", isbn)[0], "legacy")
        self.assertEqual(f.handle("reviews", isbn)[0], "new")
        f.routes["catalog"] = "new"
        self.assertEqual(f.handle("catalog", isbn)[0], "new")

    def test_compare_answers_with_legacy_and_records_mismatch(self):
        f = Facade({"catalog": "compare"})
        isbn = next(iter(legacy.BOOKS))
        old = newshop.CATALOG[isbn].price
        newshop.CATALOG[isbn].price = 1
        try:
            who, body = f.handle("catalog", isbn)
        finally:
            newshop.CATALOG[isbn].price = old
        self.assertEqual((who, body["price"]), ("legacy", 32000))
        self.assertEqual(f.compared, [("catalog", isbn, False)])


if __name__ == "__main__":
    unittest.main()
