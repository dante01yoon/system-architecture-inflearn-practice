import unittest

from idgen import EPOCH_MS, ClockMovedBackwards, Snowflake, decode, encode, parse
from shortener import Shortener, hash_code


def ticks(offsets):
    it = iter(offsets)
    return lambda: EPOCH_MS + next(it)


class Base62Test(unittest.TestCase):
    def test_round_trip(self):
        for n in (0, 1, 61, 62, 3843, 10 ** 12, 2 ** 63 - 1):
            self.assertEqual(decode(encode(n)), n)

    def test_lengths(self):
        self.assertEqual(encode(61), "Z")
        self.assertEqual(encode(62), "10")
        self.assertEqual(len(encode(62 ** 7 - 1)), 7)


class SnowflakeTest(unittest.TestCase):
    def test_same_ms_increments_sequence(self):
        g = Snowflake(5, ticks([10, 10, 11]))
        a, b, c = g.next_id(), g.next_id(), g.next_id()
        self.assertEqual([parse(x) for x in (a, b, c)], [(10, 5, 0), (10, 5, 1), (11, 5, 0)])
        self.assertTrue(a < b < c)

    def test_clock_backwards_refused(self):
        g = Snowflake(1, ticks([10, 9]))
        g.next_id()
        with self.assertRaises(ClockMovedBackwards):
            g.next_id()

    def test_sequence_overflow_waits_next_ms(self):
        g = Snowflake(1, ticks([0] * 4097 + [0, 1]))
        ids = [g.next_id() for _ in range(4097)]
        self.assertEqual(parse(ids[-1]), (1, 1, 0))
        self.assertEqual(len(set(ids)), 4097)

    def test_two_machines_never_collide(self):
        a, b = Snowflake(1, ticks([0] * 5)), Snowflake(2, ticks([0] * 5))
        ids = [a.next_id() for _ in range(5)] + [b.next_id() for _ in range(5)]
        self.assertEqual(len(set(ids)), 10)


class ShortenerTest(unittest.TestCase):
    def test_redirect_alias_expiry(self):
        t = [0]
        s = Shortener(lambda: t[0])
        a = s.create("https://a.example")
        s.create("https://b.example", alias="b")
        c = s.create("https://c.example", ttl=10)
        self.assertEqual(s.redirect(a), (302, "https://a.example"))
        self.assertEqual(s.redirect("b"), (302, "https://b.example"))
        self.assertEqual(s.redirect("nope"), (404, None))
        with self.assertRaises(ValueError):
            s.create("https://x.example", alias="b")
        t[0] = 10
        self.assertEqual(s.redirect(c), (410, None))

    def test_counter_skips_taken_alias(self):
        s = Shortener(lambda: 0)
        s.create("https://a.example", alias="1")
        self.assertEqual(s.create("https://b.example"), "2")

    def test_hash_code_fixed_length(self):
        self.assertEqual(len(hash_code("https://a.example", 7)), 7)
        self.assertEqual(hash_code("https://a.example"), hash_code("https://a.example"))


if __name__ == "__main__":
    unittest.main()
