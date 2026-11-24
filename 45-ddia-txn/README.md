# ddia-txn — 트랜잭션과 격리 수준: 갱신 손실과 write skew (파이썬 표준 라이브러리만)

DDIA 2판 8장 「Transactions」에서 다루는 주제를 서점 예제로 돌려 본다.

| 파일 | 역할 |
|---|---|
| `txn.py` | ① SQLite 연결 두 개 + 스레드로 점원 둘이 같은 책을 파는 순서를 고정(A읽기 → B읽기 → A쓰기 → B쓰기) ② 스냅샷 격리 장난감 모델 `Store`·`Txn`(버전 목록, 먼저 커밋한 쪽이 이김) |
| `demo.py` | `1` 갱신 손실과 원자적 UPDATE, `2` 계산대 근무 write skew와 두 가지 고침 |
| `solutions/signing.py` | 연습 문제 풀이(사인회 마지막 자리, 팬텀) |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
```

## 무엇이 진짜이고 무엇이 장난감인가

- `demo.py 1`은 실제 SQLite다. 다만 SQLite는 쓰는 연결을 한 번에 하나만 허락하고 트랜잭션이 직렬 가능하다(sqlite.org/isolation.html). 그래서 「읽기와 쓰기를 따로 보내는」 흔한 앱 코드 모양으로 갱신 손실을 재현한다.
- `demo.py 2`의 `Store`는 데이터베이스가 아니라 스냅샷 격리의 규칙(시작 시점 스냅샷 읽기, 같은 값을 쓴 트랜잭션끼리만 충돌)만 흉내 낸 모델이다. PostgreSQL의 Repeatable Read가 스냅샷 격리이고, write skew를 막으려면 Serializable(SSI)을 쓴다.

## 연습 문제

작가 사인회 자리가 30석, 29석이 찼다. 점원 둘이 동시에 「29명이니 한 자리 남았네」 하고 각자 손님 예약을 한 줄씩 추가하면?
`txn.py`의 장난감 모델로 재현하고, 좌석마다 줄을 미리 만들어 막아 보세요. 풀이: `python3 solutions/signing.py`
