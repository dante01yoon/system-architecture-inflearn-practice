# sdi-uber — 위치 기반 호출(파이썬 표준 라이브러리만)

서울 안에 기사 1만 명을 seed로 흩어 놓고, geohash 칸으로 가까운 기사를 찾은 뒤, 두 손님이 같은 기사를 동시에 불러도
한 명에게만 배정되게 한다. 시간은 실제로 기다리지 않고 `now` 값으로 넘긴다.

| 파일 | 역할 |
|---|---|
| `geo.py` | `encode`(geohash), `box`(칸 범위), `neighbors`(둘레 여덟 칸), `Index`(칸 → 기사, TTL 30초) |
| `match.py` | `Store.claim`(비어 있을 때만 쓰기 + 수락 리스 10초), `claim_naive`(확인하고 쓰기 — 나쁜 예), `race`(두 요청 동시에) |
| `demo.py` | `1` 반경 500m 찾기: 전부 확인 대 아홉 칸, `2` 동시 호출: 두 손님 한 기사 → 원자적 잡기 · 리스 끝 |
| `solutions/radius.py` | 연습 풀이: 반경 2km면 글자 수를 줄인다 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
```

기사 위치 범위(위도 37.45~37.65, 경도 126.85~127.15), TTL 30초, 수락 10초는 설명을 위한 가정이다. 숫자는 이 예제를 돌린 값이다.
`neighbors`는 극과 날짜 변경선 근처를 다루지 않는다.

## 연습 문제
반경을 2km로 늘리면 아홉 칸 검색이 놓치는 기사가 생기는지 확인하고, 고쳐 보세요. 풀이: `solutions/radius.py`
