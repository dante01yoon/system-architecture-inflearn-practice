"""연습 풀이: v2 버그가 100건 중 1건(1%)만 실패시키면 5% 카나리가 잡아내나. 씨앗 100개로 세어 본다.
1% 오류 = 10배 소진 → 14.4배 기준보다 느리다. SRE 실습서 표의 둘째 줄(6배)처럼 기준을 낮추고 더 오래 지켜본다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import canary  # noqa: E402

for page, watch in ((14.4, 10), (6, 60)):
    canary.PAGE, canary.WATCH = page, watch
    caught = sum(canary.rollout(0.01, seed=s)[0][5] == "되돌림" for s in range(100))
    print(f"{page}배 기준 · 5% 단계 {watch}분: 100번 중 {caught}번 잡음")
