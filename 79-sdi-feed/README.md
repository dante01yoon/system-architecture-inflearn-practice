# sdi-feed — 뉴스 피드 fan-out (파이썬 표준 라이브러리만)

사용자 100,000명과 유명인 1명(나머지 모두가 팔로우)의 팔로우 그래프를 seed로 만들고, 글을 쓸 때 팔로워 타임라인 캐시에 글 id를 퍼뜨리는 push,
타임라인을 열 때 팔로우한 사람들의 글을 모으는 pull, 유명인만 pull하는 hybrid의 쓰기·읽기 수를 센다. 타임라인은 cursor(마지막으로 본 시각)로 나눈다.

| 파일 | 역할 |
|---|---|
| `feed.py` | `graph`(seed 고정 팔로우 그래프), `Feed.post`(fan-out on write), `Feed.timeline`(캐시 + pull 글 합치기, cursor) |
| `demo.py` | `1` push·pull·hybrid의 쓰기와 읽기 수, `2` hybrid 타임라인 한 사람 합치기 |
| `solutions/unfollow.py` | 연습 풀이: 팔로우를 끊을 때 캐시에서 그 사람 글 빼기 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
```

유명인 기준 팔로워 1만 명, 캐시 200개, 한 시간 글 1,000개·열기 10,000번은 설명을 위한 가정이다. 숫자는 이 예제를 돌린 값이다(메모리 약 70MB).

## 연습 문제
팔로우를 끊으면 push로 이미 캐시에 넣어 둔 그 사람의 글은 어떻게 될까요? 끊을 때 타임라인에서 빠지게 고쳐 보세요. 풀이: `solutions/unfollow.py`
