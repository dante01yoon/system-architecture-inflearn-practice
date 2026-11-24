# resil — Bulkhead · Timeout · 재시도와 멱등성

`bulkhead.py`는 부르는 상대마다 스레드 풀을 따로 두고(`bulkheads`), 기다림에 끝을 둔다(`call_with_timeout`). `retry.py`는 지수 백오프와 지터로 다시 시도하고, `storm.py`는 손님 100명이 동시에 실패한 뒤 다시 몰리는 상황을 정해진 seed로 흉내 낸다. `payment.py`는 sqlite3 결제 서버로, 멱등성 키가 오면 첫 응답을 저장해 두고 같은 키의 재시도에는 그 응답만 돌려준다. 표준 라이브러리만 쓴다.

    python3 demo.py
    python3 -m unittest
    python3 solutions/retry_budget.py   # 연습 문제 풀이(재시도 예산, 토큰 통)
