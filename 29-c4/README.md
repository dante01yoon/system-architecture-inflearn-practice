# C4 모델 수업 예제: 서점을 지도처럼 확대하기 (파이썬 표준 라이브러리만)

온라인 서점(웹 앱 · 카탈로그 · 주문 · 결제 서비스, PostgreSQL, 외부 카드사 · 메일 발송)을 C4 모델로 적었다.

| 파일 | 역할 |
|---|---|
| `c4.py` | 사람·시스템·컨테이너·컴포넌트와 관계를 담는 `Model`, 흔한 실수 검사 `lint`, 다이어그램을 들여쓴 목록으로 `outline` |
| `bookshop.py` | 서점 모델. `bookshop(messy=True)`는 실수 세 개가 섞인 판 |
| `demo.py` | 인자 없이: 엉망인 모델과 고친 모델 검사. `1`·`2`·`3`: 그 레벨 다이어그램 |
| `solutions/courier.py` | 연습 문제 풀이 |

`lint`가 잡는 것(c4model.com/diagrams/notation 규칙에서 세 개만 골랐다):
1. 설명 없는 관계 — 선마다 무엇을 하는지 적는다
2. 기술 없는 컨테이너·컴포넌트 — Python, PostgreSQL처럼 적는다
3. 레벨 섞임 — 컨테이너 다이어그램에 컴포넌트가 끼는 식

```bash
python3 demo.py
python3 demo.py 1   # 2, 3
python3 -m unittest
```

## 연습 문제

택배사(외부 시스템)와 배송 서비스(컨테이너)를 붙이고, `lint`가 문제 0개가 되게 하세요. 컨텍스트와 컨테이너 레벨에서 어떻게 보이는지 확인합니다.
풀이: `python3 solutions/courier.py`
