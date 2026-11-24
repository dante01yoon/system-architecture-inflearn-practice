import unittest

from est import DAY, bits, estimate, rough, size


class Estimate(unittest.TestCase):
    def test_rough_keeps_one_digit(self):
        self.assertEqual(rough(1_157), 1_000)
        self.assertEqual(rough(5_787), 6_000)
        self.assertEqual(rough(11.6), 10)
        self.assertEqual(rough(0), 0)

    def test_day_is_about_ten_to_the_fifth(self):
        self.assertLess(abs(DAY - 10 ** 5) / DAY, 0.2)

    def test_units(self):
        self.assertEqual(size(1_000), '1 KB')
        self.assertEqual(size(365e9), '365 GB')
        self.assertEqual(size(5.475e15), '5.47 PB')
        self.assertEqual(bits(5.79e9), '46.3 Gbps')

    def test_review_numbers(self):
        e = estimate(10_000_000, 0.1, 100, 1_000, 5, 3, 5)
        self.assertEqual(e['per_day'], 1_000_000)
        self.assertAlmostEqual(e['write_qps'], 1_000_000 / 86_400)
        self.assertAlmostEqual(e['read_qps'], e['write_qps'] * 100)
        self.assertAlmostEqual(e['peak_read'], e['read_qps'] * 5)
        self.assertAlmostEqual(e['year'], 365e9)
        self.assertAlmostEqual(e['total'], 365e9 * 15)
        self.assertAlmostEqual(e['out'], e['read_qps'] * 1_000)

    def test_payload_scales_storage_not_qps(self):
        a = estimate(1_000, 1, 10, 1_000, 1, 1)
        b = estimate(1_000, 1, 10, 1_000_000, 1, 1)
        self.assertEqual(a['read_qps'], b['read_qps'])
        self.assertAlmostEqual(b['total'] / a['total'], 1_000)


if __name__ == "__main__":
    unittest.main()
