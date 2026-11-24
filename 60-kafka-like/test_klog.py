import tempfile
import unittest

from klog import Group, Topic


def topic():
    t = Topic(tempfile.mkdtemp(), "orders", partitions=3, segment_records=4)
    for st in ("주문됨", "결제됨", "배송됨"):
        for n in range(1, 5):
            t.append(f"order-{n}", st)
    return t


class KlogTest(unittest.TestCase):
    def test_same_key_same_partition_in_order(self):
        t = topic()
        p = t.partition_of("order-3")
        vals = [r["value"] for r in t.read(p, 0) if r["key"] == "order-3"]
        self.assertEqual(vals, ["주문됨", "결제됨", "배송됨"])
        self.assertEqual([s.name for s in t.segments(p)], ["00000000.log", "00000004.log"])

    def test_partition_goes_to_one_member_and_rebalance_resumes_from_commit(self):
        t = topic(); g = Group(t, "g")
        g.join("c1"); g.join("c2")
        owned = [p for ps in g.assignment.values() for p in ps]
        self.assertEqual(sorted(owned), [0, 1, 2])  # 겹치지 않고 빠짐없이
        total = len(g.poll("c1")) + len(g.poll("c2"))
        self.assertEqual(total, 12)
        t.append("order-7", "주문됨")
        g.join("c3")
        again = [r for m in ("c1", "c2", "c3") for _, r in g.poll(m)]
        self.assertEqual([(r["key"], r["value"]) for r in again], [("order-7", "주문됨")])  # 중복·누락 없음
        g.join("c4")
        self.assertEqual(g.assignment["c4"], [])

    def test_compaction_keeps_latest_per_key_and_offsets(self):
        t = topic()
        for k, v in (("order-7", "주문됨"), ("order-7", "결제됨"), ("order-3", "반품됨")):
            t.append(k, v)
        t.compact(2)
        recs = t.read(2, 0)
        self.assertEqual({r["key"]: r["value"] for r in recs}, {"order-3": "반품됨", "order-4": "배송됨", "order-7": "결제됨"})
        self.assertEqual([r["offset"] for r in recs], [5, 7, 8])
        self.assertEqual(t.end_offset(2), 9)


if __name__ == "__main__":
    unittest.main()
