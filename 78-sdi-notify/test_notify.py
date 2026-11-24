import unittest
from collections import Counter

from notify import MAX_TRY, Provider, Service


def note(i, ch="push", kind="tx", user="u1"):
    return {"id": i, "user": user, "to": user, "channel": ch, "kind": kind, "template": "otp", "data": {"code": 1}}


class NotifyTest(unittest.TestCase):
    def test_same_id_is_sent_once(self):
        p = Provider(0.0, 1); svc = Service({"push": p})
        self.assertEqual([svc.submit(note("a")), svc.submit(note("a"))], ["queued", "dup"])
        svc.work("push")
        self.assertEqual(p.got, ["a"])

    def test_transient_failures_retry_then_dlq(self):
        p = Provider(1.0, 1); svc = Service({"push": p})
        svc.submit(note("a"))
        self.assertEqual(svc.work("push"), MAX_TRY - 1)
        self.assertEqual((svc.status["a"], svc.dlq[0]["why"]), ("dlq", f"{MAX_TRY}번 실패"))

    def test_bad_address_goes_to_dlq_without_retry(self):
        svc = Service({"sms": Provider(0.0, 1, bad={"u1"})})
        svc.submit(note("a", "sms"))
        self.assertEqual(svc.work("sms"), 0)
        self.assertEqual(svc.dlq[0]["why"], "잘못된 주소")

    def test_flaky_provider_no_duplicates(self):
        p = Provider(0.4, 5); svc = Service({"push": p})
        for i in range(100):
            svc.submit(note(f"n{i}")); svc.submit(note(f"n{i}"))
        svc.work("push")
        self.assertTrue(all(c == 1 for c in Counter(p.got).values()))
        self.assertEqual(len(p.got) + len(svc.dlq), 100)

    def test_backoff_doubles_with_cap(self):
        svc = Service({"push": Provider(0.0, 1)})
        for k, d in [(1, 1), (2, 2), (3, 4), (9, 30)]:
            self.assertTrue(d / 2 <= svc.backoff(k) <= d)

    def test_opt_out_quiet_hours_and_limit(self):
        svc = Service({c: Provider(0.0, 1) for c in ("push", "email")}, prefs={"u1": {"off": {"email"}, "quiet": (22, 8)}}, limit=1)
        svc.now = 23 * 3600
        self.assertEqual(svc.submit(note("e", "email", "mkt")), "opt-out")
        self.assertEqual(svc.submit(note("m", "push", "mkt")), "held")
        self.assertEqual(svc.submit(note("m2", "push", "mkt")), "rate-limit")
        self.assertEqual(svc.submit(note("t", "push", "tx")), "queued")   # 거래 알림은 설정과 상관없이
        svc.work("push")
        self.assertEqual(svc.providers["push"].got, ["t", "m"])
        self.assertEqual(svc.now, 32 * 3600)                               # 다음 날 08:00

    def test_transactional_before_marketing(self):
        p = Provider(0.0, 1); svc = Service({"push": p})
        svc.submit(note("m", kind="mkt")); svc.submit(note("t"))
        svc.work("push")
        self.assertEqual(p.got, ["t", "m"])


if __name__ == "__main__":
    unittest.main()
