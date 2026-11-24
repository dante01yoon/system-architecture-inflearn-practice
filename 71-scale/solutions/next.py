"""연습 풀이: 작업자를 10대로 늘린 뒤, 캐시 적중률이 80%에서 50%로 떨어지면 어디가 먼저 막힐까?
적중이 줄면 앱 서버가 페이지를 직접 그리는 일과 복제본이 읽는 일이 함께 는다. 앱 서버가 먼저 막힌다(복제본은 아직 여유)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sim import STEPS, max_users

last = STEPS[-1][1] | {'workers': 10}
for hit in (.8, .5):
    users, neck, each = max_users(last | {'cache': hit})
    print(f"캐시 적중 {hit:.0%}: 최대 {users:,}명 · 막히는 곳: {neck} · 읽기 복제본 {each['읽기 복제본']:,}명")
