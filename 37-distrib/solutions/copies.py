"""연습 문제 풀이: 서버 한 대가 99%만 살아 있다면, 99.99% 이상이 되려면 복제본이 몇 개 필요할까?
1 - 0.01^n ≥ 0.9999 → n = 2. 단, 서로 따로 고장 난다는 가정이 깨지면(같은 건물·같은 배포) 이 계산은 너무 낙관적이다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from calc import availability, downtime_hours  # noqa: E402

for n in (1, 2, 3):
    a = availability(0.99, n)
    print(f"복제본 {n}개: {a:.6%} · 1년에 약 {downtime_hours(a) * 60:,.1f}분 멈춤")
