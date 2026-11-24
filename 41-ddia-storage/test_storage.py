import tempfile
import unittest

import layout
from btree import BTree
from lsm import LSM


def data(n=6000):
    import random
    keys = [f'k{i:05d}' for i in range(n)]
    random.Random(1).shuffle(keys)
    return [(k, 'v' * 50 + k) for k in keys]


class StorageTest(unittest.TestCase):
    def test_lsm_and_btree_return_same_values_and_latest_write_wins(self):
        lsm, bt = LSM(tempfile.mkdtemp(), limit=500), BTree()
        for k, v in data():
            lsm.put(k, v); bt.put(k, v)
        lsm.put('k00042', 'new'); bt.put('k00042', 'new')
        for k, _ in data()[:300]:
            self.assertEqual(lsm.get(k)[0], bt.get(k)[0])
        self.assertEqual(lsm.get('k00042')[0], 'new')
        lsm.flush()  # 새 값이 세그먼트로 내려가도 이긴다
        self.assertEqual(lsm.get('k00042')[0], 'new')
        self.assertIsNone(lsm.get('nope')[0])

    def test_compaction_keeps_segment_count_below_merge_at(self):
        lsm = LSM(tempfile.mkdtemp(), limit=100, merge_at=4)
        for k, v in data(2000):
            lsm.put(k, v)
        self.assertLess(len(lsm.segs), 4)
        self.assertEqual(len(list(lsm.dir.glob('*.sst'))), len(lsm.segs))

    def test_btree_writes_more_bytes_than_lsm(self):
        lsm, bt = LSM(tempfile.mkdtemp(), limit=500), BTree()
        for k, v in data():
            lsm.put(k, v); bt.put(k, v)
        self.assertGreater(bt.written, 3 * lsm.written)

    def test_column_scan_reads_fewer_bytes_same_sum(self):
        rows = layout.make(2000)
        d = tempfile.mkdtemp()
        path = layout.write_rows(rows, d); layout.write_columns(rows, d)
        r, c, z = layout.sum_rows(path), layout.sum_column(d), layout.sum_dict(d)
        self.assertEqual(r[0], sum(x[4] for x in rows))
        self.assertEqual(r[0], c[0]); self.assertEqual(r[0], z[0])
        self.assertLess(z[1], c[1]); self.assertLess(c[1], r[1] / 10)


if __name__ == '__main__':
    unittest.main()
