import unittest
from pathlib import Path

from quanta import parse, quanta

SHOP = Path(__file__).with_name("shop.txt").read_text(encoding="utf-8")


def sizes(text):
    return sorted(len(g) for g in quanta(*parse(text)))


class QuantaTest(unittest.TestCase):
    def test_shop_has_two_quanta(self):
        self.assertEqual(sizes(SHOP), [1, 5])

    def test_async_message_splits_a_quantum(self):
        text = SHOP.replace("sync   order    notify", "async  order    notify")
        self.assertEqual(sizes(text), [1, 1, 4])

    def test_shared_db_joins_services_without_calls(self):
        self.assertEqual(sizes("db d a b\nsync c e"), [2, 2])

    def test_chain_of_sync_calls_is_one_quantum(self):
        self.assertEqual(sizes("sync a b\nsync b c\nsync d c"), [4])

    def test_unknown_line_is_rejected(self):
        with self.assertRaises(ValueError):
            parse("call a b")


if __name__ == "__main__":
    unittest.main()
