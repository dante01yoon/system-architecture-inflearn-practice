import unittest

from kv import Cluster, descends, diff, merge, tree

NAMES = ["n0", "n1", "n2", "n3", "n4"]


class ClockTest(unittest.TestCase):
    def test_descends_and_concurrent(self):
        self.assertTrue(descends({"a": 2}, {"a": 1}))
        self.assertFalse(descends({"a": 2}, {"b": 1}) or descends({"b": 1}, {"a": 2}))
        self.assertEqual(merge({"a": 2}, {"a": 1, "b": 1}), {"a": 2, "b": 1})


class ClusterTest(unittest.TestCase):
    def test_preference_list_is_distinct_nodes(self):
        c = Cluster(NAMES)
        self.assertEqual(sorted(c.walk("k")), NAMES)

    def test_hinted_handoff_then_delivery(self):
        c = Cluster(NAMES); want = c.walk("k")[:3]
        c.nodes[want[1]].up = False
        ok, log, _ = c.put("k", "v")
        self.assertTrue(ok)
        self.assertIn(want[1], [to for _, to in log])
        self.assertEqual(c.recover(want[1]), 1)
        self.assertEqual(c.nodes[want[1]].data["k"][0][0], "v")
        self.assertEqual(sum(len(n.hints) for n in c.nodes.values()), 0)

    def test_write_fails_below_w(self):
        c = Cluster(NAMES[:3], w=3)
        c.nodes["n0"].up = False
        self.assertFalse(c.put("k", "v")[0])

    def test_concurrent_writes_kept_then_merged(self):
        c = Cluster(NAMES); o = c.walk("k")
        _, _, base = c.put("k", [])
        c.put("k", ["a"], base, coord=o[0]); c.put("k", ["b"], base, coord=o[1])
        _, vs, ctx = c.get("k")
        self.assertEqual(sorted(v[0] for v, _ in vs), ["a", "b"])
        c.put("k", ["a", "b"], ctx)
        self.assertEqual([v for v, _ in c.get("k")[1]], [["a", "b"]])

    def test_merkle_finds_only_differing_ranges(self):
        c = Cluster(NAMES); a, b = c.nodes["n0"], c.nodes["n1"]
        keys = [f"k{i:03d}" for i in range(256)]
        for k in keys:
            a.store(k, 1, {"x": 1}); b.store(k, 1, {"x": 1})
        self.assertEqual(diff(tree(a, keys), tree(b, keys))[0], [])
        a.store("k100", 2, {"x": 2})
        self.assertEqual(diff(tree(a, keys), tree(b, keys))[0], [100 // 16])


if __name__ == "__main__":
    unittest.main()
