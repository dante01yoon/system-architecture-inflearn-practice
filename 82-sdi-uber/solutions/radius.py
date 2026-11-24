"""연습 풀이: 반경이 칸보다 크면 아홉 칸으로는 모자란다 → 반경에 맞는 글자 수를 고른다.
python3 solutions/radius.py (sdi-uber 폴더에서)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from demo import GANGNAM, seoul  # noqa: E402
from geo import Index, box, dist, encode  # noqa: E402


def precision_for(p, r):
    """칸의 짧은 변이 반경 이상인 가장 긴 글자 수."""
    for n in range(9, 0, -1):
        s, nn, w, e = box(encode(*p, n))
        if min(dist((s, w), (s, e)), dist((s, w), (nn, w))) >= r:
            return n
    return 1


src = seoul()
for n in (6, precision_for(GANGNAM, 2000)):
    idx = Index(n)
    for d, (q, seen) in src.pos.items():
        idx.update(d, *q, seen)
    a, b = idx.brute(GANGNAM, 2000, 5), idx.nearby(GANGNAM, 2000, 5)
    print(f"글자 {n}: 반경 2km 전부 {len(a)}명 · 아홉 칸 {len(b)}명 · 같음 {a == b}")
