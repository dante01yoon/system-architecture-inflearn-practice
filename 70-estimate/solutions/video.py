"""연습 풀이: 사진 대신 30초 영상(10 MB 가정)을 붙인다면? 같은 DAU · 비율에서 저장과 대역폭만 열 배씩 는다.
가장 몰릴 때 나감이 수백 Gbps라, 서버에서 바로 내보내지 않고 CDN 같은 앞단에서 내준다는 설계로 이어진다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from demo import COPIES, DAU, PEAK, RATIO, WRITES, YEARS
from est import bits, estimate, rough, size

e = estimate(DAU, WRITES, RATIO, 1_000 + 10_000_000, YEARS, COPIES, PEAK)
print(f"저장 1년 {size(e['year'])} · {YEARS}년 × {COPIES}벌 = 어림 {size(rough(e['total']))}")
print(f"가장 몰릴 때 나감 {size(e['peak_out'])}/s = {bits(e['peak_out'])}")
