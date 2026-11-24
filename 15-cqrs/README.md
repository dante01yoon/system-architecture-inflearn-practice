# CQRS 수업 예제 (파이썬 표준 라이브러리만)

온라인 서점의 주문을 쓰기 DB와 읽기 DB(둘 다 SQLite)로 나눈다.

| 파일 | 역할 |
|---|---|
| `bookshop/commands.py` | 쓰기 쪽. `PlaceOrder` 커맨드와 처리 함수(재고 규칙, 이벤트 기록) |
| `bookshop/projector.py` | 이벤트를 읽어 읽기 DB를 화면 모양으로 채운다 |
| `bookshop/queries.py` | 읽기 쪽. 읽기 DB에서 그대로 꺼낸다 |
| `demo.py` | 주문 → 바로 조회(아직 없음) → 프로젝터 → 다시 조회 |
| `bench.py` | 같은 화면을 JOIN으로 / 읽기 DB에서 꺼낼 때 걸린 시간 |
| `solutions/best_sellers.py` | 연습 문제 풀이 |

```bash
python3 demo.py
python3 bench.py
python3 test_cqrs.py
```

## 연습 문제

`책별 판매 권수` 읽기 모델을 하나 더 붙인다. `commands.py`는 고치지 않는다.
풀이: `python3 -m solutions.best_sellers`
