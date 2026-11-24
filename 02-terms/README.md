# 용어 수업 예제: 결합도를 눈으로 세기 (파이썬 표준 라이브러리만)

같은 온라인 서점(주문·결제·재고·메일)을 두 가지로 짰다.

| 폴더·파일 | 역할 |
|---|---|
| `shop_tight/` | 촘촘한 결합. 모듈들이 서로의 함수를 직접 부른다 |
| `shop_loose/` | 느슨한 결합. 주문은 이벤트만 남기고(`events.py`), 나머지는 듣는다 |
| `coupling.py` | `ast`로 소스를 읽어 같은 패키지 모듈끼리의 import를 센다 |
| `demo.py` | 두 서점의 import 화살표 수, `payment.py`를 고치면 영향이 닿는 모듈 수 |
| `solutions/shop_tight_fixed/` | 연습 문제 풀이 |

```bash
python3 demo.py
python3 coupling.py shop_tight
python3 -m unittest
```

## 연습 문제

`shop_tight`에서 import 화살표를 두 개 이상 끊어 보세요. 기능은 그대로 둡니다.
풀이: `python3 coupling.py solutions/shop_tight_fixed` (화살표 7개 → 5개)
