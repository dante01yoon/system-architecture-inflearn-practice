# sdi-api — API와 통신 방식 (파이썬 표준 라이브러리만)

서점 REST API를 `http.server`로 127.0.0.1:8921에 띄우고, 페이지네이션 두 방식과 재시도에 안전한 메서드를 직접 부른다.
실시간 알림은 짧은 폴링과 롱 폴링을 시간 계산으로 흉내 내어 요청 수와 지연을 비교한다.

| 파일 | 역할 |
|---|---|
| `api.py` | `GET /v1/books`(offset 또는 cursor), `POST /v1/books`(새 책), `PUT /v1/wishlist/{id}`, `POST /v1/orders`(Idempotency-Key 지원), `serve()` |
| `poll.py` | `arrivals`(seed 고정 도착 시각), `short_poll`, `long_poll` |
| `demo.py` | `1` offset 대 cursor, `2` PUT 대 POST 재시도와 멱등성 키, `3` 짧은 폴링 대 롱 폴링 |
| `solutions/delete.py` | 연습 문제 풀이(DELETE도 멱등인지) |

```bash
python3 demo.py 1
python3 demo.py 2
python3 demo.py 3
python3 -m unittest
```

숫자는 이 예제를 돌린 값이다. 폴링 비교는 실제로 기다리지 않고 시간을 계산한다(네트워크 왕복 0.2초 가정).

## 연습 문제
위시리스트에서 책을 빼는 `DELETE /v1/wishlist/{id}`를 더하고, 같은 요청을 두 번 보내도 결과가 같은지 확인하라. 풀이: `python3 solutions/delete.py`
