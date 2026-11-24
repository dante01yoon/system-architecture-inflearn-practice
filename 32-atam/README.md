# atam — 미니 유틸리티 트리와 민감 지점·트레이드오프 지점

`tree.py`: 서점의 유틸리티 트리(품질 → 세부 → 시나리오, 시나리오마다 중요도·어려움 H/M/L)와 설계 결정(품질마다 +1 좋아짐 / -1 나빠짐)을 데이터로 둔다.
`ranked`는 (중요도, 어려움) 높은 순, `classify`는 품질 둘 이상을 반대로 움직이면 트레이드오프 지점·아니면 민감 지점, `risks`는 (H,H) 시나리오의 품질을 깎는 결정을 위험 후보로 뽑는다.
분류 규칙은 Kazman·Klein·Clements, 「ATAM: Method for Architecture Evaluation」(CMU/SEI-2000-TR-004, 2000) 7.2절의 정의를 단순화한 것이다. 숫자(+1/-1)는 설명용으로 정한 값이다. 표준 라이브러리만 쓴다.

    python3 demo.py
    python3 -m unittest
    python3 solutions/add_cache.py   # 연습 문제 풀이: 캐시 결정 더하기
