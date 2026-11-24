import unittest

import canary
from migrate import STEPS, run, shop, work


class CanaryTest(unittest.TestCase):
    def test_good_version_goes_all_the_way(self):
        rows = canary.rollout(0.0003)
        self.assertEqual([r[0] for r in rows], [5, 25, 50, 100])
        self.assertEqual(rows[-1][5], "완료")

    def test_bad_version_rolls_back_at_first_step(self):
        rows = canary.rollout(0.20)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][5], "되돌림")
        self.assertGreaterEqual(rows[0][4], canary.PAGE)

    def test_canary_limits_damage(self):
        self.assertLess(canary.rollout(0.20)[0][2] * 10, canary.big_bang(0.20) * 2)


class MigrateTest(unittest.TestCase):
    def test_six_steps_no_errors_no_mismatch(self):
        db, truth = shop()
        self.assertTrue(all(e == 0 and b == 0 for _, _, e, b in run(db, truth)))
        cols = [r[1] for r in db.execute("PRAGMA table_info(books)")]
        self.assertEqual(cols, ["id", "title", "price_krw"])

    def test_direct_rename_breaks_old_app(self):
        db, truth = shop()
        db.execute("ALTER TABLE books RENAME COLUMN price TO price_krw")
        self.assertEqual(work(db, truth, "v1", 0), (1, 0))

    def test_skipping_backfill_gives_wrong_reads(self):
        db, truth = shop()
        steps = STEPS[:2] + [("읽기 바꾸기", None, ["v3"])]   # 채우기를 건너뜀
        self.assertGreater(run(db, truth, steps, rounds=1)[-1][3], 0)

    def test_switching_reads_while_v1_writes_gives_wrong_reads(self):
        db, truth = shop()
        steps = STEPS[:3] + [("읽기 바꾸기", None, ["v1", "v3"])]
        self.assertGreater(run(db, truth, steps)[-1][3], 0)


if __name__ == "__main__":
    unittest.main()
