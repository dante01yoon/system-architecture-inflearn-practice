"""연습 풀이: 파트너마다 1분에 N번까지만 받고, 넘으면 429를 돌려준다(고정 창 — 장난감)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from signing import Verifier, make_request  # noqa: E402


class LimitedVerifier(Verifier):
    def __init__(self, keys, now, per_minute):
        super().__init__(keys, now)
        self.per_minute, self.count = per_minute, {}

    def check(self, req):
        code, who = super().check(req)
        if code != 200:
            return code, who
        slot = (who, int(self.now() // 60))
        self.count[slot] = self.count.get(slot, 0) + 1
        if self.count[slot] > self.per_minute:
            return 429, f"{who} 1분 한도 {self.per_minute}번 초과"
        return 200, who


if __name__ == "__main__":
    t = [1_763_100_000]
    api = LimitedVerifier({"k1": ("partner-a", b"s")}, lambda: t[0], per_minute=3)
    codes = [api.check(make_request("k1", b"s", "GET", "/orders", b"", t[0], f"n{i}"))[0] for i in range(5)]
    print(codes)
    assert codes == [200, 200, 200, 429, 429]
