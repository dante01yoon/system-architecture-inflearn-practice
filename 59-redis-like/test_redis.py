import subprocess
import sys
import threading
import unittest

import client
import demo
from client import Client
from server import run

PORT = 8897   # 데모(8899)와 겹치지 않게


class CommandTest(unittest.TestCase):
    def test_commands(self):
        self.assertEqual(run("INCR t:a"), "1")
        self.assertEqual(run("INCR t:a"), "2")
        self.assertEqual(run("GET t:none"), "(nil)")
        self.assertEqual(run("KEYS t:*"), "1")

    def test_naive_counter_loses_updates(self):
        self.assertEqual(demo.naive_counter(), 1)


class ServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = subprocess.Popen([sys.executable, "server.py", str(PORT)])
        client.PORT = PORT
        Client(PORT).close()                              # 뜰 때까지 기다림

    @classmethod
    def tearDownClass(cls):
        cls.srv.terminate(); cls.srv.wait()

    def test_concurrent_incr_is_exact(self):
        def work():
            c = Client(PORT); c.cmd("INCR n"); c.close()
        ts = [threading.Thread(target=work) for _ in range(200)]
        [t.start() for t in ts]; [t.join() for t in ts]
        self.assertEqual(Client(PORT).cmd("GET n"), "200")

    def test_keys_blocks_but_scan_yields(self):
        c = Client(PORT); c.cmd("FILL 300000")
        demo.Client = lambda: Client(PORT)
        _, took, keys_wait = demo.worst(lambda: c.cmd("KEYS user:*"))
        (n, total), _, scan_wait = demo.worst(lambda: demo.scan_all(c))
        self.assertEqual(total, 300000)
        self.assertGreater(keys_wait, took / 2)           # GET이 KEYS 대부분을 기다렸다
        self.assertLess(scan_wait, keys_wait / 5)


if __name__ == "__main__":
    unittest.main()
