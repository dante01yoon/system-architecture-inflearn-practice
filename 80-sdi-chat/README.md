# sdi-chat — 채팅 시스템 (파이썬 표준 라이브러리만)

채팅 서버를 한 프로세스 안에 asyncio로 작게 흉내 낸다. WebSocket 연결을 들고 있는 연결 서버 두 대(A·B), 누가 어느 서버에 붙어 있는지 적는 기록부,
대화마다 번호를 1씩 올려 순서를 정하는 저장소, 오프라인 사용자의 보관함과 푸시 알림, 받는 쪽 중복 거르기, 하트비트 접속 표시가 들어 있다.
실제 네트워크는 쓰지 않는다(`asyncio.sleep`으로 한 번 건너기를 흉내).

| 파일 | 역할 |
|---|---|
| `chat.py` | `Registry`(사용자 → 연결 서버), `Store.append`(대화별 번호 · client_id로 보낸 쪽 재시도 거르기), `Client.receive`(번호로 중복 버림), `ConnServer.push`(ack가 없으면 다시 보냄), `Chat.send`·`deliver`(저장 → fan-out 또는 보관함+푸시), `beat`·`online`(하트비트) |
| `demo.py` | `1` 다른 서버 사이 전달 · 오프라인 보관함 · 다시 연결, `2` 그룹 fan-out · ack 유실과 중복 거르기 · 보낸 쪽 재시도, `3` 하트비트 접속 표시 |
| `solutions/read_receipt.py` | 연습 풀이: 그룹 읽음 표시(사용자마다 「여기까지 읽음」 번호 하나) |

```bash
python3 demo.py 1
python3 demo.py 2
python3 demo.py 3
python3 -m unittest
```

하트비트 5초 · 15초 시간 초과, ack 재시도 3번은 설명을 위한 가정이다.

## 연습 문제
그룹 채팅에 읽음 표시를 붙여 보세요. 메시지마다 누가 읽었는지 저장하지 말고, 사용자마다 대화별로 「여기까지 읽음」 번호 하나만 저장해서 「읽음 1/2」를 계산합니다. 풀이: `solutions/read_receipt.py`
