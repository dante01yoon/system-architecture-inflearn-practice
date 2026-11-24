"""연습 풀이: 지연 SLO(요청의 99%가 1초 안에)를 더하면 호출이 언제 울리나."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from incident import minutes  # noqa: E402
from methods import PAGE, burn  # noqa: E402

LOG = minutes()
LATENCY_SLO = 99.0   # 1초 안에 끝난 요청 비율 목표 %


def latency_burn(t, window=5):
    xs = [LOG[k]["slow"] for k in range(max(0, t - window + 1), t + 1)]
    return sum(xs) / len(xs) / (100 - LATENCY_SLO)


avail = next(t for t in range(20) if burn(LOG, t) >= PAGE)
lat = next(t for t in range(20) if latency_burn(t) >= PAGE)
print(f"가용성 SLO 호출 {avail}분 · 지연 SLO 호출 {lat}분 ({latency_burn(lat):.1f}배) → {avail - lat}분 먼저")
