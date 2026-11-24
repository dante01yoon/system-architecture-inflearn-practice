# ddia-trouble — 분산 시스템에서 믿을 수 없는 것들

서점 결제·가격·재고로 네트워크, 시계, 프로세스 멈춤을 흉내 낸다. 시간은 밀리초·초 숫자로 다루고(실제 네트워크·시계를 쓰지 않음), 지연·어긋남 숫자는 설명을 위한 가정이다. 파이썬 표준 라이브러리만 쓴다.

| 파일 | 역할 |
|---|---|
| `net.py` | `call`: 요청 사라짐 · 응답 사라짐 · 느림이 손님에게는 모두 타임아웃으로 보임, `PaymentServer`(멱등성 키) |
| `clock.py` | `WallClock`(어긋남 · NTP 되감기) · `MonotonicClock` · `lww_merge`(도장이 큰 쓰기만 남김) |
| `lock.py` | `LockService`(리스 + 1씩 커지는 토큰) · `Storage`(펜싱: 옛 토큰 거절) |
| `demo.py` | `1` 네트워크, `2` 시계와 LWW, `3` 멈춤과 펜싱 토큰 |
| `solutions/lamport_lww.py` | 연습 문제 풀이 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 demo.py 3
python3 -m unittest
```

실제 파이썬에서 벽시계는 `time.time()`, 단조 시계는 `time.monotonic()`이다(https://docs.python.org/3/library/time.html).

## 연습 문제

demo 2에서 관리자2는 36,000원을 본 뒤에 32,400원으로 고쳤는데도 LWW가 32,400원을 버렸습니다. 벽시계 대신 노드마다 세는 번호(램포트 시계)로 도장을 찍어, 앞 쓰기를 본 뒤의 쓰기가 늘 이기게 고쳐 보세요.
풀이: `python3 solutions/lamport_lww.py`
