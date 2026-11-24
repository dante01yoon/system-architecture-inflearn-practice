# USE와 RED 예제: 서점 10분치 지표 (파이썬 표준 라이브러리만)

seed 고정으로 서점 10분치 지표를 초마다 만든다. 5분째부터 외부 결제 API가 느려지고(0.2초 → 2.4초), `/checkout`은 DB 연결을 쥔 채 결제를 기다린다.
나머지 엔드포인트(`/books`, `/search`, `/cart`)는 캐시에서 답한다. CPU·메모리·네트워크·디스크 값은 평소 수준으로 둔 가정이다.

| 파일 | 역할 |
|---|---|
| `metrics.py` | `seconds`(초마다 요청 목록 + 자원 표본), `checkout`(연결 풀에서 줄 서기, 리틀의 법칙) |
| `methods.py` | `red`(엔드포인트마다 Rate·Errors·Duration p99), `use`(자원마다 Utilization·Saturation·Errors), `suspicious`(Gregg의 기준) |
| `demo.py` | `1` RED 표로 아픈 서비스 찾기, `2` USE 점검표로 그 안의 자원 찾기 |
| `solutions/release_early.py` | 연습 문제 풀이 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
```

## 연습 문제

결제 API를 부르기 전에 DB 연결을 돌려주도록 바꾸면 USE 표와 RED 표가 어떻게 바뀌는지 확인해 보세요(`seconds(hold_while_paying=False)`).
풀이: `python3 solutions/release_early.py`
