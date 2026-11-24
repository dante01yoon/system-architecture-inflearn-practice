import unittest

from chash import Ring, load, mod_n, moved

KEYS = [f"k{i}" for i in range(20_000)]
N4 = ["n0", "n1", "n2", "n3"]


class RingTest(unittest.TestCase):
    def test_moved_keys_only_go_to_new_node(self):
        a, b = Ring(N4, 100), Ring(N4 + ["n4"], 100)
        changed = [k for k in KEYS if a.node_for(k) != b.node_for(k)]
        self.assertTrue(changed)
        self.assertTrue(all(b.node_for(k) == "n4" for k in changed))

    def test_ring_moves_far_less_than_mod_n(self):
        ring = moved(KEYS, Ring(N4, 100).node_for, Ring(N4 + ["n4"], 100).node_for)
        modn = moved(KEYS, lambda k: mod_n(k, N4), lambda k: mod_n(k, N4 + ["n4"]))
        self.assertLess(ring, 0.3)
        self.assertGreater(modn, 0.7)

    def test_vnodes_even_out_load(self):
        c = load(KEYS, Ring(N4, 100).node_for)
        self.assertLess(max(c.values()) / min(c.values()), 1.3)

    def test_remove_only_moves_removed_nodes_keys(self):
        r = Ring(N4, 50)
        before = {k: r.node_for(k) for k in KEYS}
        r.remove("n2")
        self.assertTrue(all(r.node_for(k) == v for k, v in before.items() if v != "n2"))

    def test_replicas_distinct_and_start_at_owner(self):
        r = Ring(N4, 100)
        rep = r.replicas("order:42", 3)
        self.assertEqual(len(set(rep)), 3)
        self.assertEqual(rep[0], r.node_for("order:42"))

    def test_wraps_around(self):
        r = Ring(["a"], 1)
        self.assertEqual(r.node_for("anything"), "a")


if __name__ == "__main__":
    unittest.main()
