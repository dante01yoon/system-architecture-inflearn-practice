# fitness — 피트니스 함수: 아키텍처 규칙을 자동 검사로

`bookshop/`: 세 층(web → orders → pricing|storage). `fitness.py`: 피트니스 함수 넷을 CI처럼 PASS/FAIL로 찍고 하나라도 FAIL이면 종료 코드 1.
- layers: 아래 층이 위 층을 import하면 실패(ast로 읽음, 실행하지 않음)
- no-cycles: 모듈 import 그래프에서 깊이 우선 탐색으로 순환 찾기
- p95-latency: `pricing.quote`를 timeit으로 100번 재서 95번째 값이 예산(2ms) 안인지
- file-size: bookshop 파일 하나가 40줄을 넘으면 실패

`.importlinter`는 같은 층 규칙을 실제 도구 import-linter(pypi `import-linter`, 명령 `lint-imports`)의 layers 계약으로 적은 것이다. 여기서는 설치하지 않고 표준 라이브러리 `fitness.py`만 돌린다. 실제 도구의 layers 계약은 간접 import(다른 모듈을 거친 사슬)까지 본다 — `fitness.py`는 직접 import만 본다.

    python3 demo.py
    python3 fitness.py
    python3 -m unittest
    python3 solutions/independence.py   # 연습 문제 풀이: 같은 층끼리 서로 모르게
