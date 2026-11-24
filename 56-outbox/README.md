# outbox — Transactional Outbox: 주문 저장과 이벤트 발행을 함께 (파이썬 표준 라이브러리만)

| 파일 | 역할 |
|---|---|
| `outbox.py` | SQLite `orders`·`outbox` 표, 그냥 저장 후 발행(`place_naive`), 한 트랜잭션에 저장(`place`·`cancel`), 폴링 전달자, 로그 테일링 흉내, 이벤트 id로 중복을 거르는 소비자, 정리 |
| `demo.py` | `1` 죽는 자리 셋(발행 전 · 커밋 뒤 · 전달자가 보낸 뒤 표시 전), `2` 폴링 전달자 대 로그 테일링(둘 다 커밋 순서) |
| `solutions/cancel_consumer.py` | 연습 풀이(취소 이벤트로 예약 풀기, 중복 취소는 한 번만) |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
```

## 무엇이 진짜이고 무엇이 흉내인가

- 브로커는 파이썬 리스트, 「서버가 죽음」은 `Crash` 예외다.
- 로그 테일링: 진짜는 DB 트랜잭션 로그(MySQL binlog, PostgreSQL WAL)를 읽는다(예: Debezium Outbox Event Router). 여기서는 `outbox`에 행이 들어올 때 트리거가 `txlog`에 한 줄을 남기고, 전달자가 오프셋으로 따라 읽는다.
- 소비자의 처리한 id 목록은 메모리 집합이다. 실서비스는 처리 결과와 같은 트랜잭션에 저장한다.
