# 실시간 베스트셀러 순위표 (파이썬 표준 라이브러리만)

모의 면접 문제 「온라인 서점 베스트셀러 순위표(실시간 Top-K)」를 작게 만든다. 주문 흐름은 정해 둔 씨앗으로 만드는 가짜 데이터다
(책 50,000권, 지프 분포, 90분 동안 200,000건, 60분부터 신간 「책99999」이 주문의 30%).

| 파일 | 역할 |
|---|---|
| `stream.py` | `purchases()` — (초, 책 번호) 주문 흐름 |
| `topk.py` | `Window`(1분 칸 60개 창), `Leaderboard`(책 번호로 나눈 샤드 4개 · 핫 책은 돌아가며 나눠 쓰기 · 샤드별 상위 k를 힙으로 합치기), `exact_top` |
| `sketch.py` | `CountMin`(줄 4 × 칸 2,000, `hashlib.blake2b`) |
| `demo.py` | `1` 샤드 쓰기 수 · 60분/90분 순위 · 정확한 답과 비교, `2` count-min 추정 대 정확 · 칸 수 |
| `solutions/genre.py` | 연습 문제 풀이 예시 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
```

## 연습 문제
분야별 순위표를 더해 보세요. 책 번호 끝자리로 분야 열 개를 정하고, 분야마다 상위 3권을 보여 주면 됩니다. 풀이 예시: `solutions/genre.py`
