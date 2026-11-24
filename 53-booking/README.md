# booking — 선착순 예약: 300석에 30,000명 (파이썬 표준 라이브러리만)

숫자는 모두 **가정한 값**이다: 300석, 10시 정각부터 10초 동안 30,000명(평균 1초 지수 분포, seed 7), 읽고 나서 쓰기까지 1ms.

| 파일 | 역할 |
|---|---|
| `booking.py` | 도착 시각 만들기, sqlite3 재고 표, ① 읽고·확인하고·쓰기(`naive_read`·`naive_write`) ② 조건부 UPDATE 한 문장(`atomic_reserve`, 멱등성 키) ③ 대기실(`waiting_room`, 도착 순 번호표·초당 N명) |
| `demo.py` | `1` 초과 판매와 조건부 UPDATE, `2` 대기실과 멱등성 키 |
| `solutions/rates.py` | 연습 문제 풀이(입장 속도별 기다림과 부하) |

```bash
python3 demo.py 1     # 10초 안팎
python3 demo.py 2
python3 -m unittest
```

`run_threads`는 도착 시각을 1ms 칸으로 묶고, 같은 칸의 요청을 스레드 3개가 나눠 「모두 읽은 뒤 모두 쓴다」(Barrier). 그래서 실행할 때마다 결과가 같다. 진짜 서비스의 겹침은 이보다 들쭉날쭉하다.
Redis를 쓴다면 재고 숫자를 `DECR`로 줄일 수 있다(redis.io/docs/latest/commands/decr). 다만 `DECR`은 0 아래로도 내려가니, 돌려받은 값이 음수면 매진으로 보고 되돌려야 한다.

## 연습 문제

대기실의 초당 입장 수를 50·100·200·400·1000으로 바꿔 보며, 데이터베이스 부하와 기다림 p99가 어떻게 바뀌는지 표로 만들어 보세요. 풀이: `python3 solutions/rates.py`
