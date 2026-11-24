"""연습 문제 풀이: 손님을 최대 1초만 기다리게 하려면 줄 한도는? Little의 법칙 L = λW = 100건/초 × 1초 = 100칸."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim import simulate  # noqa: E402

for limit in (300, 100):
    r = simulate(limit)
    print(f"줄 한도 {limit}칸: 성공 {r['done']:,} · 거절 {r['rejected']:,} · 최대 대기 {r['max_wait']:.1f}초")
