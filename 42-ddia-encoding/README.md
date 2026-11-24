# ddia-encoding — 인코딩과 스키마 진화

서점 주문 하나를 JSON과, 필드 번호 · 길이 · 값으로 적는 작은 바이너리 인코딩(`struct`)으로 바꿔 본다.
프로토콜 버퍼의 「필드 번호」 생각만 흉내 낸 교육용 형식이다(실제 프로토콜 버퍼 바이트와 다름). 파이썬 표준 라이브러리만 쓴다.

| 파일 | 역할 |
|---|---|
| `codec.py` | 스키마 `V1`·`V2`(새 필드 `gift_wrap` = 번호 5), `encode`, `decode`(모르는 번호는 건너뛰고, 없는 필드는 기본값) |
| `demo.py` | `1` JSON 대 바이너리 · 큰 숫자 · Base64, `2` 상위·하위 호환, `3` 이름 바꾸기 대 번호 바꾸기 |
| `solutions/remove_field.py` | 연습 문제 풀이 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 demo.py 3
python3 -m unittest
```

## 연습 문제

v3에서 `customer` 필드(번호 2)를 지우세요. v2와 v3가 서로의 데이터를 읽을 수 있어야 하고,
나중에 누가 번호 2를 다른 필드에 다시 쓰지 못하게 막아야 합니다. 풀이: `python3 solutions/remove_field.py`
