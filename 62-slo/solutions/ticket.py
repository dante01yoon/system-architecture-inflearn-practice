"""연습 풀이: SRE Workbook 표의 셋째 줄(3일 창 · 6시간 짧은 창 · 소진 속도 1 → 티켓)을 더해, 천천히 새는 문제도 잡는다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import slo  # noqa: E402

# 매일 0.2%씩 조금 새는 한 달(소진 속도 약 2배, 호출 기준엔 안 걸림)
rows = [(t, c, s + (1 if i % 5 == 0 else 0)) for i, (t, c, s) in enumerate(slo.month())]
print("호출(page) 기준만:", len(slo.alerts(rows)), "번")
slo.PAGE.append((3 * 1440, 360, 1.0))
fired = slo.alerts(rows)
print("티켓 줄을 더하면:", slo.clock(fired[0][0]), "에 처음 울림" if fired else "안 울림")
assert fired
