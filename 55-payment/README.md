# payment — 결제는 됐는데 주문이 안 끝났다

가짜 결제 대행사(PG)와 우리 주문 서비스로, 외부 결제와 우리 DB 사이의 틈을 흉내 낸다. 파이썬 표준 라이브러리만 쓴다(sqlite3 메모리 DB). PG의 동작은 설명용 가정이며 실제 어느 회사의 내부 동작이 아니다.

| 파일 | 역할 |
|---|---|
| `pg.py` | `FakePG`: 멱등성 키로 결제 · 고장 넣기(`timeout_after_charge` 결제 뒤 응답 끊김, `duplicate_webhook`, `lost_webhook`, `lookup_down`) · 웹훅 보내기 · 조회 · 환불 · 정산 보고서 |
| `orders.py` | `OrderService`: 상태 기계(PENDING → PAID → CONFIRMED / FAILED / REFUND_NEEDED → REFUNDED) · 조건부 UPDATE + 감사 로그 · 웹훅(이벤트 ID로 중복 무시) · 폴링 · 대사(reconcile) |
| `demo.py` | `1` 고장 세 가지와 멈춘 주문, `2` 대사 작업이 찾아서 고치기 |
| `solutions/our_side_only.py` | 연습 문제 풀이 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
```

## 연습 문제

지금 대사 작업은 PG 정산 보고서를 기준으로 우리 주문을 봅니다. 거꾸로, 우리는 CONFIRMED인데 PG 보고서에는 없는 주문을 찾는 검사를 더해 보세요.
풀이: `python3 solutions/our_side_only.py`
