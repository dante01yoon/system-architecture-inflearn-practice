# seat — 좌석 선점과 만료, 중복 판매 막기

작가 사인회 좌석을 sqlite3 파일 하나로 판다. 파이썬 표준 라이브러리만 쓴다. 시간은 밖에서 넣는 초 숫자다(`Clock`).

| 파일 | 역할 |
|---|---|
| `seat.py` | `race`: 50명이 좌석 10개에 동시에 · 방법 넷(`buy_naive` 확인하고 쓰기, `buy_locked` 비관적 잠금 `BEGIN IMMEDIATE`, `buy_version` 낙관적 버전, `buy_unique` UNIQUE 제약) / `hold` 선점(만료된 선점은 다시 잡힘) · `view` 손님 화면 · `pay` 선점 번호 검사 + 멱등성 키 · `sweep` 청소 작업 |
| `demo.py` | `1` 동시에 사기, `2` 선점 · 만료 · 늦은 결제 · 두 번 누르기 |
| `solutions/hold_many.py` | 연습 문제 풀이 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
```

`THINK = 0.1`초는 읽고 쓰는 사이의 네트워크 왕복을 흉내 낸 가정이다(경쟁이 매번 보이게). SQLite에는 `SELECT … FOR UPDATE`가 없어서 `BEGIN IMMEDIATE`(처음부터 쓰기 잠금)로 대신한다. PostgreSQL에서는 `SELECT … FOR UPDATE`가 그 줄을 잠근다(https://www.postgresql.org/docs/current/explicit-locking.html).

## 연습 문제

친구와 나란히 앉으려고 B-7과 B-8을 함께 선점합니다. 둘 중 하나라도 이미 선점 중이면 하나도 잡지 않게 `hold_many`를 만들어 보세요.
풀이: `python3 solutions/hold_many.py`
