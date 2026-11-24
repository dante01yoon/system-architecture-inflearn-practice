import os
import tempfile
import unittest

from txn import Conflict, cashier_store, clerks, leave, on_duty, open_db, sell_atomic, sell_read_then_write, stock


class LostUpdateTest(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(tempfile.mkdtemp(), "t.db")

    def test_read_then_write_loses_one_sale(self):
        open_db(self.path, 10)
        clerks(self.path, sell_read_then_write)
        self.assertEqual(stock(self.path), 9)

    def test_atomic_update_keeps_both_sales(self):
        open_db(self.path, 10)
        clerks(self.path, sell_atomic)
        self.assertEqual(stock(self.path), 8)

    def test_atomic_update_never_goes_negative(self):
        open_db(self.path, 1)
        log = clerks(self.path, sell_atomic)
        self.assertEqual(stock(self.path), 0)
        self.assertEqual(sum("품절" in line for line in log), 1)


class WriteSkewTest(unittest.TestCase):
    def both(self, lock_row):
        db = cashier_store()
        a, b = db.begin(), db.begin()
        leave(a, "민지", lock_row); leave(b, "준호", lock_row)
        a.commit()
        try:
            b.commit()
        except Conflict:
            pass
        return on_duty(db.begin())

    def test_snapshot_isolation_allows_write_skew(self):
        self.assertEqual(self.both(False), 0)

    def test_shared_row_turns_skew_into_conflict(self):
        self.assertEqual(self.both(True), 1)

    def test_snapshot_reads_ignore_later_commits(self):
        db = cashier_store()
        old = db.begin()
        t = db.begin(); t.write("근무:민지", 0); t.commit()
        self.assertEqual(on_duty(old), 2)
        self.assertEqual(on_duty(db.begin()), 1)


if __name__ == "__main__":
    unittest.main()
