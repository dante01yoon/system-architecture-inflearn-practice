# 요청 수 제한(Rate Limiter) 알고리즘 다섯 가지 (파이썬 표준 라이브러리만)

token bucket, leaky bucket(미터로 쓰는 물통), fixed window counter, sliding window log, sliding window counter를 같은 인터페이스(`allow()`)로 만들고,
가짜 시계를 넣어 같은 요청 줄에 돌려 본다. `store.py`는 여러 서버가 같이 쓰는 카운터에서 「읽고 비교하고 쓰기」가 한도를 넘기는 경쟁을 보여 준다.

| 파일 | 역할 |
|---|---|
| `limiters.py` | `TokenBucket`(+`retry_after`), `LeakyBucket`, `FixedWindow`, `SlidingLog`, `SlidingCounter` — 모두 `clock`을 받는다 |
| `store.py` | `Store`(get · set · incr), `check_then_set`(겹친 읽기 → 덮어쓰기), `incr_then_check`(INCR 먼저) |
| `demo.py` | `1` 창 경계 몰림(seed 7), `2` 토큰 통 다시 차기, `3` 같은 카운터의 경쟁 |
| `solutions/headers.py` | 연습 문제 풀이: 사용자마다 토큰 통 · 429 · Retry-After · 남은 횟수 헤더 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 demo.py 3
python3 -m unittest
```

## 연습 문제
사용자마다 토큰 통을 하나씩 두고, 통과하면 200과 남은 횟수, 막히면 429와 Retry-After를 돌려주는 작은 게이트웨이를 만들어 보세요. 풀이: `solutions/headers.py`
