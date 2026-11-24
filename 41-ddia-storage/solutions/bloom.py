"""연습 문제 풀이: 세그먼트마다 블룸 필터를 붙이면, 없는 키를 찾을 때 파일을 열지 않고 건너뛴다."""
import hashlib
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lsm import LSM  # noqa: E402


class Bloom:
    def __init__(self, keys, bits=8192, k=4):
        self.bits, self.k, self.v = bits, k, 0
        for key in keys:
            for h in self._hashes(key):
                self.v |= 1 << h

    def _hashes(self, key):
        d = hashlib.sha256(key.encode()).digest()
        return [int.from_bytes(d[i * 4:i * 4 + 4], 'big') % self.bits for i in range(self.k)]

    def maybe(self, key):  # False면 확실히 없다, True면 있을 수도 있다
        return all(self.v >> h & 1 for h in self._hashes(key))


lsm = LSM(tempfile.mkdtemp(), limit=1500)
for i in range(50_000):
    lsm.put(f'book:{i:06d}', 'x')
blooms = [Bloom(keys, bits=len(keys) * 10) for keys, _, _ in lsm.segs]
miss = [f'nope:{i}' for i in range(10_000)]
plain = sum(lsm.get(k)[1] for k in miss)
opened = sum(b.maybe(k) for k in miss for b in blooms)
print(f'없는 키 {len(miss):,}번: 필터 없이 파일 {plain:,}번 열기 → 필터로 {opened:,}번')
