# redis-like — 스레드 하나짜리 이벤트 루프 키-값 서버

Redis가 명령을 스레드 하나로 실행하는 방식을 파이썬 표준 라이브러리(`selectors`)로 작게 흉내 낸다. 진짜 Redis 프로토콜(RESP)이 아니라 한 줄 글자 명령이고, `KEYS`는 키 목록 대신 개수만 돌려준다.

| 파일 | 역할 |
|---|---|
| `server.py` | 이벤트 루프(`selectors` → epoll · kqueue), 명령 `INCR` · `GET` · `FILL` · `KEYS` · `SCAN`. 기본 포트 8899, 127.0.0.1만 |
| `client.py` | 한 줄 보내고 한 줄 받는 손님 |
| `demo.py` | `1` 스레드 200개 동시 INCR(잠금 없이 정확), `2` 느린 KEYS가 GET을 막고 SCAN은 사이사이 양보 |
| `solutions/pipeline.py` | 연습 문제 풀이 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
```

시간 숫자는 컴퓨터마다 다르다.

## 연습 문제

명령을 하나 보내고 답을 기다리기를 1000번 하는 대신, 1000개를 한꺼번에 보내고 답을 모아 읽어 보세요(파이프라이닝). 걸린 시간을 비교합니다.
풀이: `python3 solutions/pipeline.py`
