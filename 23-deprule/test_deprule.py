import tempfile
import unittest
import shutil
from pathlib import Path

import checker
from bookshop.main import build
from bookshop.usecases import OrderRequest

HERE = Path(__file__).parent


class DependencyRuleTest(unittest.TestCase):
    def test_project_follows_the_rule(self):
        self.assertEqual(checker.check(HERE), [])

    def test_inner_importing_outer_is_caught(self):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(HERE / "bookshop", Path(tmp, "bookshop"))
            p = Path(tmp, "bookshop/entities.py")
            p.write_text("import sqlite3\n" + p.read_text())
            self.assertEqual(checker.check(tmp), ["bookshop/entities.py:1 sqlite3"])

    def test_outer_importing_inner_is_fine(self):
        self.assertIsNone(checker.ring("json"))
        self.assertLess(checker.ring("bookshop.entities"), checker.ring("bookshop.adapters.memory_repo"))

    def test_both_adapters_give_same_results(self):
        results = []
        for kind in ["memory", "sqlite"]:
            place = build(kind)
            results.append([place(OrderRequest("9780134494166", 2)), place(OrderRequest("9780134494166", 2))])
        self.assertEqual(results[0], results[1])
        self.assertEqual((results[0][0].ok, results[0][0].total, results[0][1].ok), (True, 64000, False))


if __name__ == "__main__":
    unittest.main()
