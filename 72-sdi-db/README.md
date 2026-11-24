# 데이터베이스 고르기와 인덱스 (파이썬 표준 라이브러리만)

`sqlite3` 메모리 DB에 주문 200,000줄을 넣고, 인덱스가 없을 때 · 한 칸 인덱스 · 묶음 인덱스 `(user_id, day)`에서 같은 질의가 하는 일을
`EXPLAIN QUERY PLAN`과 가상 머신 명령 수(실행마다 같음), 걸린 시간(조금씩 다름)으로 비교한다. 키로만 읽는 모양은 `dict`(키-값)와 견준다.
`decide.py`는 면접 문제 넷의 읽기·쓰기 모양을 받아 DB 종류를 이유와 함께 고른다(이 강의가 정한 단순한 규칙).

| 파일 | 역할 |
|---|---|
| `db.py` | `build`(주문 표), `plan`(EXPLAIN QUERY PLAN), `work`(명령 수 · ms) |
| `decide.py` | `RULES`, `suggest(needs)`, `PROBLEMS`(URL 단축기 · 채팅 · 친구 프로필 · 상품 검색) |
| `demo.py` | `1` 인덱스 효과, `2` 키-값 대 SQL 훑기, `3` 문제 넷의 DB 고르기 |
| `solutions/day_index.py` | 연습 문제 풀이 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 demo.py 3
python3 -m unittest
```

## 연습 문제
묶음 인덱스 `(user_id, day)`만 있을 때 `WHERE day = ?` 질의는 SCAN이 됩니다. 이 질의가 인덱스를 타게 하고, 그 대가를 한 줄로 적어 보세요. 풀이: `solutions/day_index.py`
