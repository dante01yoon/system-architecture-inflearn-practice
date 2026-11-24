# ddia-replication — 리더-팔로워와 복제 지연, 쿼럼

서점 리뷰를 리더에 쓰고, 비동기 팔로워(지연을 밀리초로 흉내, seed 고정)에서 읽는다. 파이썬 표준 라이브러리만 쓴다.
네트워크·지연 숫자는 설명을 위한 가정이다.

| 파일 | 역할 |
|---|---|
| `replica.py` | `Leader`(복제 로그) · `Follower`(lag 뒤에 로그를 적용, `position`) |
| `session.py` | `read_your_writes`(내가 쓴 번호까지 따라온 곳에서만 읽기) · `sticky`(사용자마다 같은 팔로워) |
| `quorum.py` | 리더 없는 복제: n개 중 w개에 쓰고 r개에서 읽어 버전이 가장 큰 값 |
| `demo.py` | `1` read-your-writes, `2` monotonic reads, `3` 쿼럼 w + r > n |
| `solutions/consistent_prefix.py` | 연습 문제 풀이 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 demo.py 3
python3 -m unittest
```

## 연습 문제

손님 질문과 판매자 답이 서로 다른 샤드에 저장돼 서로 다른 팔로워로 복제됩니다. 답이 질문보다 먼저 보이는 상황(consistent prefix reads 깨짐)을 만들고, 고쳐 보세요.
풀이: `python3 solutions/consistent_prefix.py`
