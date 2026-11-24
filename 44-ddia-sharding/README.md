# ddia-sharding — 샤딩: 키 범위 대 해시, 재균형, 인기 키 (파이썬 표준 라이브러리만)

온라인 서점 주문 2만 건(seed 고정)을 샤드 4개에 나눠 본다. DDIA 2판 7장 「Sharding」에서 다루는 주제를 따라간다.

| 파일 | 역할 |
|---|---|
| `shard.py` | `orders`(주문 만들기), `range_bounds`·`by_range`(키 범위), `by_hash`(해시), `moved_mod_n`(해시 mod N 재균형), `assign`·`moved_fixed`(고정 파티션 64개), `salted`(인기 키 흩기) |
| `demo.py` | `1` 키 범위 대 해시 분포 · 오늘 주문 핫스팟 · 범위 조회, `2` 샤드 4→5개 때 옮길 키, `3` 인기 작가 키와 salting |
| `solutions/secondary.py` | 연습 문제 풀이(로컬 대 글로벌 보조 인덱스) |

```bash
python3 demo.py 1
python3 demo.py 2
python3 demo.py 3
python3 -m unittest
```

해시는 파이썬 `hash()`가 아니라 md5를 쓴다(`hash()`는 실행마다 값이 바뀐다). 숫자는 이 예제를 돌린 값이지 실제 서비스 측정이 아니다.

## 연습 문제

「작가007의 주문을 모두 보여 줘」를 빠르게 하고 싶다. 주문은 주문 번호 해시로 샤딩돼 있다.
작가 색인을 샤드마다 따로 두면(로컬) 몇 샤드에 묻게 될까? 색인 자체를 작가로 샤딩하면(글로벌)? 각각 쓸 때 무엇을 치르나?
풀이: `python3 solutions/secondary.py`
