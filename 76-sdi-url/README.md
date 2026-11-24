# URL 단축기와 고유 ID (파이썬 표준 라이브러리만)

긴 URL을 짧은 코드로 바꾸는 단축기를 작게 만든다. 카운터 값을 base62로 바꾸는 방식, URL 해시를 잘라 쓰는 방식,
Twitter Snowflake 비슷한 64비트 ID(41비트 시각 · 10비트 기계 · 12비트 순번, 이 예제의 시작 시각은 2026-01-01 UTC)를 비교한다.

| 파일 | 역할 |
|---|---|
| `idgen.py` | `encode`/`decode`(base62), `Snowflake`(같은 1ms 안 순번, 시계가 뒤로 가면 `ClockMovedBackwards`), `parse` |
| `shortener.py` | `hash_code`(SHA-256 앞부분 → base62 k글자), `Shortener`(카운터 · 직접 고른 이름 · 만료, `redirect` → 302/404/410) |
| `demo.py` | `1` Snowflake ID, `2` base62 길이, `3` 해시 자르기 겹침(URL 100만 개, seed 7), `4` 짧은 주소 만들고 열기 |
| `solutions/key_range.py` | 연습 문제 풀이: 서버마다 카운터 범위를 미리 받아 쓰기 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 demo.py 3
python3 demo.py 4
python3 -m unittest
```

## 연습 문제
중앙 카운터 하나에 매번 묻지 않도록, 서버가 번호 1,000개짜리 범위를 한 번에 받아 쓰게 바꿔 보세요. 서버 세 대가 코드 1만 개를 만들 때 겹침이 없고 중앙 호출이 몇 번인지 확인합니다. 풀이: `solutions/key_range.py`
