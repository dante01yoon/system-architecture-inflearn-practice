# crosscut — 횡단 관심사를 한 곳에서 (파이썬 표준 라이브러리만)

| 파일 | 역할 |
|---|---|
| `before.py` | 서점 핸들러 셋이 로그·시간 재기·인증·에러 처리·요청 id를 각자 반복한다 |
| `after.py` | 같은 핸들러 + WSGI(PEP 3333) 모양 미들웨어 줄(`with_request_id`·`errors`·`auth`·`access_log`), 데코레이터(`timed`, 나쁜 예 `swallow`), `contextvars` 요청 id, 로그 `Filter` |
| `demo.py` | `1` 흩어진 줄 세기 + 요청 id가 붙은 로그, `2` 미들웨어 순서(토큰 새는 로그)와 예외 삼키기 |
| `solutions/response_id.py` | 연습 문제 풀이 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
```

토큰 `tok-demo-7f3a9c`는 예제용 가짜 값이다. 실제 서버는 `wsgiref`·gunicorn 같은 WSGI 서버가 `environ`과 `start_response`를 넘겨준다(여기서는 함수로 직접 부른다).

## 연습 문제

요청 id를 응답 헤더 `X-Request-Id`로 돌려주는 미들웨어를 만들어 보세요. 미들웨어 줄의 어디에 둬야 할까요? 풀이: `python3 solutions/response_id.py`
