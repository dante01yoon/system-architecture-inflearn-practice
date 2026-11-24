# pattern — 같은 문제, 두 패턴, 서로 다른 결과

느린 원격 가격 조회(`price_service.py`, 한 번에 200ms로 친다)를 두 패턴으로 푼다.
- `cache_aside.py`: 부르는 쪽이 캐시를 확인하고, 없으면 원격에서 가져와 넣는다. 값을 바꿀 때는 원본을 바꾼 뒤 캐시를 지운다.
- `read_through.py`: 데코레이터가 원본 앞에 캐시를 세운다. 부르는 쪽은 캐시를 모르고, 값은 TTL 동안 캐시에 남는다.

`demo.py`는 화면 20번(책 두 권 번갈아), 6번째 화면 직전에 할인가로 바꾸는 상황에서 패턴마다 원격 호출 수와 옛 가격을 보여 준 횟수를 센다. 파이썬 표준 라이브러리만 쓴다.

    python3 demo.py
    python3 -m unittest
    python3 solutions/write_through.py   # 연습 문제 풀이(write-through)
