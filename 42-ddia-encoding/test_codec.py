import json
import unittest

from codec import V1, V2, decode, encode
from demo import ORDER


class CodecTest(unittest.TestCase):
    def test_round_trip_and_smaller_than_json(self):
        data = encode(ORDER, V1)
        self.assertEqual(decode(data, V1), (ORDER, []))
        self.assertLess(len(data), len(json.dumps(ORDER).encode()))

    def test_forward_compat_old_reader_skips_new_tag(self):
        got, skipped = decode(encode({**ORDER, "gift_wrap": True}, V2), V1)
        self.assertEqual((got, skipped), (ORDER, [5]))

    def test_backward_compat_new_reader_defaults_missing(self):
        got, _ = decode(encode(ORDER, V1), V2)
        self.assertEqual(got, {**ORDER, "gift_wrap": False})

    def test_rename_is_safe_but_changing_tag_loses_data(self):
        data = encode(ORDER, V1)
        self.assertEqual(decode(data, {**V1, 4: ("amount", "int")})[0]["amount"], 57600)
        moved = {k: v for k, v in V1.items() if k != 4} | {6: ("total", "int")}
        got, skipped = decode(data, moved)
        self.assertEqual((got["total"], skipped), (0, [4]))


if __name__ == "__main__":
    unittest.main()
