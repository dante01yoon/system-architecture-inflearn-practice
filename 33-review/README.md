# review — 가벼운 아키텍처 리뷰 체크리스트

`checklist.py`: 서점 리뷰 질문 아홉 개(영역 여덟: 동인·결정·장애·데이터·관측·보안·비용·되돌리기, 영향 H/M/L). `answers.py`: 팀의 답(yes/partial/no + 메모, 답 없으면 no).
`scorer.py`: 심각도 = 영향(H3·M2·L1) × 모자람(yes0·partial1·no2), 6 이상 높음·3 이상 중간·나머지 낮음, 높은 순 정렬. 점수 규칙은 설명용으로 정한 값이다.
영역은 AWS Well-Architected(6 pillars)·Azure Well-Architected(5 pillars)의 기둥과 ATAM의 품질 시나리오를 서점 크기에 맞게 줄인 것이다. 표준 라이브러리만 쓴다.

    python3 demo.py
    python3 -m unittest
    python3 solutions/add_question.py   # 연습 문제 풀이: 질문 하나 더하기
