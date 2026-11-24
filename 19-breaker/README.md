# breaker — Circuit Breaker: 장애가 번지지 않게 끊기

`breaker.py`의 `CircuitBreaker`는 실패가 `threshold`번 이어지면 열려(open) 부르지 않고 바로 대신할 답(fallback)을 돌려주고, `reset_timeout`초가 지나면 반쯤 열림(half_open)에서 한 번만 시험해 성공하면 닫힌다(closed). 시계는 바꿔 끼울 수 있어서 `review.py`의 가짜 시계로 실제로 기다리지 않고 기다린 시간만 센다. 표준 라이브러리만 쓴다.

    python3 demo.py
    python3 -m unittest
    python3 solutions/failure_rate.py   # 연습 문제 풀이(실패 비율로 열기)
