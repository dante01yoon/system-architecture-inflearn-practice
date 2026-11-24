"""연습 문제 풀이: 캐시 적중률이 몇 %까지 떨어져도 DB가 넘치지 않을까? (앱 8대 · 풀 12)
DB가 1초에 할 수 있는 일 4,000ms ≥ 읽기 950 × (1 - 적중률) × 5ms + 쓰기 50 × 10ms → 적중률 ≥ 약 26%."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim import run  # noqa: E402

for hit in (0.0, 0.2, 0.25, 0.3, 0.5, 0.9):
    r = run(servers=8, pool=12, hit=hit)
    print(f"적중률 {hit:>4.0%}: DB 사용률 {r['db_use']:>5.0%} · p95 {r['p95']:>7.0f}ms")
