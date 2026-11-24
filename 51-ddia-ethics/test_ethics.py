import unittest

from demo import RAW
from privacy import SECRET, minimize, pseudonym
from shred import KeyStore, read_personal, toy_decrypt, toy_encrypt, write_order


class EthicsTest(unittest.TestCase):
    def test_minimize_keeps_only_purpose_fields(self):
        e = minimize(RAW[0], "판매 통계")
        self.assertEqual(list(e), ["user", "book", "price", "day"])
        self.assertNotIn("minji", str(e))

    def test_pseudonym_stable_and_key_dependent(self):
        self.assertEqual(pseudonym("minji"), pseudonym("minji"))
        self.assertNotEqual(pseudonym("minji"), pseudonym("junho"))
        self.assertNotEqual(pseudonym("minji"), pseudonym("minji", b"other"))

    def test_toy_cipher_roundtrip(self):
        k = b"k" * 32
        blob = toy_encrypt(k, "김민지")
        self.assertNotIn("김민지".encode(), blob)
        self.assertEqual(toy_decrypt(k, blob), "김민지")

    def test_shredding_one_user_keeps_others_and_aggregates(self):
        log, keys = [], KeyStore()
        for r in RAW:
            write_order(log, keys, pseudonym(r["user_id"], SECRET), r["book"], r["price"], r["day"], r["name"], r["address"])
        before = [dict(e) for e in log]
        keys.forget(pseudonym("minji", SECRET))
        self.assertEqual(log, before)                                # 로그는 그대로
        self.assertIsNone(read_personal(keys, log[0], "name"))
        self.assertEqual(read_personal(keys, log[1], "name"), "이준호")
        self.assertEqual(sum(e["price"] for e in log), 104000)


if __name__ == "__main__":
    unittest.main()
