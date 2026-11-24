import io
import logging
import threading
import unittest

import after
import demo


class Capture:
    def __enter__(self):
        self.buf = io.StringIO()
        h = logging.StreamHandler(self.buf)
        h.addFilter(after.AddRequestId())
        h.setFormatter(logging.Formatter("rid=%(rid)s %(message)s"))
        after.log.handlers[:] = [h]
        after.log.setLevel(logging.INFO)
        after.log.propagate = False
        return self

    def __exit__(self, *a):
        after.log.handlers[:] = []

    @property
    def lines(self):
        return self.buf.getvalue().splitlines()


class CrosscutTest(unittest.TestCase):
    def setUp(self):
        after.STOCK["ddia"] = 3
        after.charge = lambda user, amount: None

    def test_handlers_have_no_crosscutting_lines(self):
        self.assertGreater(demo.count("before.py")[0], 20)
        self.assertEqual(demo.count("after.py")[:1], (0,))
        self.assertEqual(demo.count("after.py")[2], 0)

    def test_every_line_of_one_request_shares_one_id(self):
        app = after.make_app(after.with_request_id, after.errors, after.auth, after.access_log)
        with Capture() as c:
            demo.call(app, "/orders"); demo.call(app, "/orders")
        ids = [line.split()[0] for line in c.lines]
        self.assertEqual(len(set(ids[:len(ids) // 2])), 1)
        self.assertNotEqual(ids[0], ids[-1])
        self.assertNotIn("rid=-", ids)

    def test_threads_keep_their_own_request_id(self):
        seen, gate = {}, threading.Barrier(2)

        def work(name):
            after.request_id.set(name)
            gate.wait()                      # 둘 다 값을 넣은 뒤에 읽는다
            seen[name] = after.request_id.get()
        ts = [threading.Thread(target=work, args=(n,)) for n in ("a", "b")]
        [t.start() for t in ts]; [t.join() for t in ts]
        self.assertEqual(seen, {"a": "a", "b": "b"})

    def test_logging_outside_auth_leaks_token(self):
        with Capture() as c:
            demo.call(after.make_app(after.with_request_id, after.access_log, after.auth), "/books")
        self.assertIn("tok-demo-7f3a9c", c.lines[0])
        with Capture() as c:
            demo.call(after.make_app(after.with_request_id, after.auth, after.access_log), "/books")
        self.assertNotIn("tok-demo", c.buf.getvalue())
        self.assertIn("****9c", c.lines[0])

    def test_missing_token_is_401(self):
        app = after.make_app(after.with_request_id, after.auth)
        self.assertEqual(demo.call(app, "/books", token="nope"), "401")

    def test_swallowing_hides_failure_and_errors_middleware_reports_it(self):
        def fail(user, amount):
            raise ConnectionError
        app = after.make_app(after.with_request_id, after.errors, after.auth)
        after.charge = after.swallow(fail)
        with Capture():
            self.assertEqual(demo.call(app, "/orders"), "201")
        after.charge = fail
        with Capture() as c:
            self.assertEqual(demo.call(app, "/orders"), "500")
        self.assertIn("event=error type=ConnectionError", c.lines[-1])

    def test_chain_order_first_is_outermost(self):
        calls = []

        def mark(name):
            def m(app):
                def mw(env, sr):
                    calls.append(name)
                    return app(env, sr)
                return mw
            return m
        after.chain(lambda e, s: [b""], mark("a"), mark("b"))({}, None)
        self.assertEqual(calls, ["a", "b"])


if __name__ == "__main__":
    unittest.main()
