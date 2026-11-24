import unittest

from trap import deepest, diagnose, load, lockstep, shared_dbs


class TrapTest(unittest.TestCase):
    def test_always_together_is_lockstep(self):
        deploys = [["a", "b"], ["a", "b"], ["a", "b", "c"], ["c"]]
        self.assertEqual(lockstep(deploys), [("a", "b", 3)])

    def test_sometimes_together_is_not(self):
        deploys = [["a", "b"], ["a", "b"], ["a", "b"], ["a"]]
        self.assertEqual(lockstep(deploys), [])

    def test_chain_follows_longest_path_and_survives_cycles(self):
        calls = {"a": ["b", "x"], "b": ["c"], "c": ["a"]}
        self.assertEqual(deepest(calls, "a"), ["a", "b", "c"])

    def test_shared_db(self):
        self.assertEqual(shared_dbs({"a": "d1", "b": "d1", "c": "d2"}), {"d1": ["a", "b"]})

    def test_example_configs(self):
        bad, good = diagnose(load("distributed.json")), diagnose(load("fixed.json"))
        self.assertEqual(bad["lockstep"], [("order", "stock", 5)])
        self.assertEqual(bad["chains"], [["order", "catalog", "stock", "payment"]])
        self.assertEqual(bad["shared"], {"shop_db": ["order", "stock"]})
        self.assertEqual(good, {"lockstep": [], "chains": [], "shared": {}})


if __name__ == "__main__":
    unittest.main()
