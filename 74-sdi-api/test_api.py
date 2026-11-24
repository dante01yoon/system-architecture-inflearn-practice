import json
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import api
from poll import arrivals, long_poll, short_poll

PORT = 8931   # 녹화가 쓰는 8921과 겹치지 않게


def call(method, path, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    with urlopen(Request(f"http://127.0.0.1:{PORT}{path}", data=data, method=method, headers=headers or {})) as r:
        return r.status, json.loads(r.read())


class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = api.serve(PORT)

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def setUp(self):
        api.reset()

    def test_offset_repeats_after_insert_cursor_does_not(self):
        a = call("GET", "/v1/books?offset=0&limit=5")[1]["items"]
        call("POST", "/v1/books")
        b = call("GET", "/v1/books?offset=5&limit=5")[1]["items"]
        self.assertEqual(set(a) & set(b), {46})
        api.reset()
        first = call("GET", "/v1/books?limit=5")[1]
        call("POST", "/v1/books")
        b = call("GET", f"/v1/books?cursor={first['next_cursor']}&limit=5")[1]["items"]
        self.assertEqual(set(first["items"]) & set(b), set())
        self.assertEqual(b, [45, 44, 43, 42, 41])

    def test_cursor_walks_whole_list(self):
        seen, cur = [], None
        while True:
            r = call("GET", "/v1/books?limit=7" + (f"&cursor={cur}" if cur else ""))[1]
            seen += r["items"]
            cur = r["next_cursor"]
            if cur is None:
                break
        self.assertEqual(seen, list(range(50, 0, -1)))

    def test_put_is_idempotent_post_is_not(self):
        for _ in range(2):
            call("PUT", "/v1/wishlist/7")
        self.assertEqual(api.STATE["wishlist"], {7})
        for _ in range(2):
            call("POST", "/v1/orders", {"book_id": 7})
        self.assertEqual(len(api.STATE["orders"]), 2)

    def test_idempotency_key_replays_first_answer(self):
        h = {"Idempotency-Key": "k"}
        s1, r1 = call("POST", "/v1/orders", {"book_id": 7}, h)
        s2, r2 = call("POST", "/v1/orders", {"book_id": 7}, h)
        self.assertEqual((s1, s2), (201, 200))
        self.assertEqual(r1, r2)
        self.assertEqual(len(api.STATE["orders"]), 1)

    def test_unknown_path_404(self):
        with self.assertRaises(HTTPError) as e:
            call("PUT", "/v1/wishlist/abc")
        self.assertEqual(e.exception.code, 404)


class PollTest(unittest.TestCase):
    def test_short_poll_counts(self):
        r, e, d = short_poll([1.0, 2.0, 12.0], 5, 60)
        self.assertEqual((r, e), (12, 10))
        self.assertAlmostEqual(d, (4 + 3 + 3) / 3)

    def test_long_poll_beats_short_poll_latency(self):
        t = arrivals(12, 3600)
        self.assertLess(long_poll(t, 30, 3600)[2], 0.5)
        self.assertGreater(short_poll(t, 30, 3600)[2], 5)

    def test_long_poll_empty_when_nothing_happens(self):
        r, e, _ = long_poll([999.0], 30, 300)
        self.assertEqual(r, e)


if __name__ == "__main__":
    unittest.main()
