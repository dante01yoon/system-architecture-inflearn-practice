# 시스템 디자인 면접 답변 틀 (파이썬 표준 라이브러리만)

일곱 걸음(기능 요구 → 비기능 요구 → 어림셈 → 핵심 엔티티 → API → 큰 그림 → 깊게 파기)에 무게를 주고, 면접 시간을 정수 분으로 나눈 시간표와
문제마다 빈 연습지(마크다운)를 만든다. 처음 인사 2분·끝 질문 3분은 따로 둔 가정이다. 무게는 Hello Interview Delivery Framework의 걸음별 권장 분을 참고해 정한 값이다.

| 파일 | 역할 |
|---|---|
| `frame.py` | `STEPS`(이름·무게·끝날 때 손에 있을 것), `timeline(total)`, `worksheet(problem)` |
| `demo.py` | `1` 45분 시간표, `2` 60분 시간표, `3` 위시리스트 연습지(`wishlist.md`) 만들기 |
| `solutions/wishlist_filled.md` | 연습 문제 풀이 예시 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 demo.py 3
python3 -m unittest
```

## 연습 문제
`python3 demo.py 3`으로 만든 `wishlist.md`를 일곱 걸음 순서대로, 시간표의 분을 지키며 채워 보세요. 풀이 예시: `solutions/wishlist_filled.md`
