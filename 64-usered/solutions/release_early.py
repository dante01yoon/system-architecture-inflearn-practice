"""연습 풀이: 결제 API를 부르기 전에 DB 연결을 돌려주면(연결은 0.03초만 쥠) 풀과 /checkout이 어떻게 바뀌나."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from methods import red, use  # noqa: E402
from metrics import seconds  # noqa: E402

for name, log in (("지금", seconds()), ("연결 먼저 반납", seconds(hold_while_paying=False))):
    u, s, e = use(log[300:])["DB 연결 풀"]
    rate, err, d = red(log[300:])["/checkout"]
    print(f"{name}: 풀 사용률 {u:.0f}% · 줄 {s:.1f} · /checkout 오류율 {err:.1f}% · p99 {d:,.0f}ms")
print("→ 결제가 느린 건 그대로라 p99는 결제 시간만큼 남는다(타임아웃·서킷 브레이커로 따로 다룬다)")
