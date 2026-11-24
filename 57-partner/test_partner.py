import unittest

from signing import Verifier, make_request
from tokens import Issuer, check

T = 1_000_000
BODY = b'{"qty": 1}'


class SigningTest(unittest.TestCase):
    def setUp(self):
        self.clock = [T]
        self.api = Verifier({"k1": ("a", b"s1"), "k2": ("a", b"s2")}, lambda: self.clock[0])

    def req(self, key="k1", secret=b"s1", ts=T, nonce="n1", body=BODY):
        return make_request(key, secret, "POST", "/orders", body, ts, nonce)

    def test_valid_then_replay(self):
        r = self.req()
        self.assertEqual(self.api.check(r), (200, "a"))
        self.assertEqual(self.api.check(r)[1], "이미 쓴 nonce (재전송)")

    def test_tampered_body_path_and_wrong_secret(self):
        self.assertEqual(self.api.check(dict(self.req(), body=b'{"qty": 9}'))[0], 401)
        self.assertEqual(self.api.check(dict(self.req(), path="/admin"))[0], 401)
        self.assertEqual(self.api.check(self.req(secret=b"x"))[1], "서명 불일치")

    def test_stale_or_future_timestamp(self):
        self.assertEqual(self.api.check(self.req(ts=T - 301))[1], "시각이 5분 밖")
        self.assertEqual(self.api.check(self.req(ts=T + 301))[1], "시각이 5분 밖")

    def test_unsigned_request_does_not_burn_nonce(self):
        self.api.check(self.req(secret=b"x"))
        self.assertEqual(self.api.check(self.req())[0], 200)

    def test_two_active_keys_then_retire(self):
        self.assertEqual(self.api.check(self.req("k2", b"s2", nonce="n2"))[0], 200)
        del self.api.keys["k1"]
        self.assertEqual(self.api.check(self.req(nonce="n3"))[1], "모르는 키")


class TokenTest(unittest.TestCase):
    def setUp(self):
        self.clock = [T]
        self.now = lambda: self.clock[0]
        self.clients = {"a": {"secrets": ["s"], "scopes": {"orders:read"}}}
        self.auth = Issuer(b"k", self.clients, self.now)

    def test_scope_least_privilege(self):
        tok, _ = self.auth.token("a", "s", "orders:read")
        self.assertEqual(check(b"k", tok, "orders:read", self.now), (200, "a"))
        self.assertEqual(check(b"k", tok, "orders:write", self.now)[0], 403)
        self.assertEqual(self.auth.token("a", "s", "orders:write"), (None, "invalid_scope"))

    def test_bad_client_tamper_audience_expiry(self):
        self.assertEqual(self.auth.token("a", "nope", "orders:read")[1], "invalid_client")
        tok, _ = self.auth.token("a", "s", "orders:read")
        self.assertEqual(check(b"other", tok, "orders:read", self.now)[0], 401)
        other, _ = self.auth.token("a", "s", "orders:read", aud="stock-api")
        self.assertEqual(check(b"k", other, "orders:read", self.now)[1], "다른 서비스용 토큰")
        self.clock[0] += 600
        self.assertEqual(check(b"k", tok, "orders:read", self.now)[1], "만료")

    def test_secret_rotation(self):
        self.clients["a"]["secrets"].append("s2")
        self.assertIsNotNone(self.auth.token("a", "s2", "orders:read")[0])
        self.clients["a"]["secrets"].remove("s")
        self.assertEqual(self.auth.token("a", "s", "orders:read")[1], "invalid_client")


if __name__ == "__main__":
    unittest.main()
