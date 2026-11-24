# sdi-chash — 안정 해시(consistent hashing) (파이썬 표준 라이브러리만)

주문 키 10만 개를 노드 4대에 나누고, 5대로 늘릴 때 옮길 키와 노드마다 받은 키 수를 잰다.

| 파일 | 역할 |
|---|---|
| `chash.py` | `h`(md5 해시), `mod_n`, `Ring`(고리 · 가상 노드 · `node_for` · `replicas`), `moved`, `load` |
| `demo.py` | `1` 노드 4→5대: mod N 대 고리 대 고리+가상 노드 100개, `2` 가상 노드 1개 대 100개의 고른 정도와 복제 자리 |
| `solutions/weighted.py` | 연습 문제 풀이(성능이 두 배인 노드에 가상 노드 두 배) |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
```

해시는 파이썬 `hash()`가 아니라 md5를 쓴다(`hash()`는 실행마다 값이 바뀐다). 숫자는 이 예제를 돌린 값이다.

## 연습 문제
노드 하나가 다른 노드보다 성능이 두 배다. 고리에서 이 노드가 키를 두 배쯤 받게 하려면 무엇을 바꾸면 될까? 풀이: `python3 solutions/weighted.py`
