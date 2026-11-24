"""서점에서 들은 증상 넷을 패턴 지도에 넣어 본다."""
from patmap import answer

SYMPTOMS = [
    "주문 내역 화면 조회가 무겁고, 쓰는 표와 모양이 달라요",
    "추천 서비스가 느려지면 주문까지 멈춰요",
    "주문과 결제가 여러 서비스에 걸친 트랜잭션이에요",
    "연말 세일에 주문이 한꺼번에 몰려요",
]

import sys

# 녹화 터미널은 19줄 — 1은 증상 1~2, 2는 증상 3~4(인자 없으면 넷 다)
part = sys.argv[1] if len(sys.argv) > 1 else ''
for i, s in enumerate(SYMPTOMS, 1):
    if part == '1' and i > 2 or part == '2' and i < 3:
        continue
    print(f"{i}) {s}")
    print("\n".join(answer(s)))
