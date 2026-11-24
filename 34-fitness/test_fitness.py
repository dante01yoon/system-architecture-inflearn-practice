import shutil
import tempfile
import unittest
from pathlib import Path

import fitness

HERE = Path(__file__).parent


def broken(edit):
    tmp = tempfile.mkdtemp()
    shutil.copytree(HERE / "bookshop", Path(tmp, "bookshop"))
    path, text = edit
    p = Path(tmp, "bookshop", path)
    p.write_text(text + p.read_text())
    return tmp


class FitnessTest(unittest.TestCase):
    def test_current_commit_passes(self):
        self.assertTrue(all(ok for _, ok, _ in fitness.run(HERE)))

    def test_upward_import_breaks_layers_and_makes_cycle(self):
        tmp = broken(("orders.py", "from bookshop.web import render\n"))
        g = fitness.graph(tmp)
        self.assertEqual(fitness.upward(g), ["orders.py:1 -> bookshop.web"])
        self.assertEqual(fitness.cycle(g)[0], fitness.cycle(g)[-1])
        shutil.rmtree(tmp)

    def test_cycle_found_in_plain_graph(self):
        self.assertEqual(fitness.cycle({"a": {"b": 1}, "b": {"a": 1}}), ["a", "b", "a"])
        self.assertIsNone(fitness.cycle({"a": {"b": 1}, "b": {}}))

    def test_same_layer_is_allowed(self):
        self.assertEqual(fitness.upward({"bookshop.pricing": {"bookshop.storage": 1}}), [])

    def test_big_file_fails(self):
        tmp = broken(("web.py", "#\n" * 50))
        size = dict((n, ok) for n, ok, _ in fitness.run(tmp))["file-size"]
        self.assertFalse(size)
        shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
