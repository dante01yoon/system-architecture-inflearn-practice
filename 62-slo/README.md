# slo — SLI·SLO·Error Budget: 서점 결제 30일 기록으로 계산하기 (파이썬 표준 라이브러리만)

| 파일 | 역할 |
|---|---|
| `slo.py` | seed 고정 30일 분 단위 요청 기록(전체·4xx·5xx), SLI(좋은/유효), 에러 버짓, 소진 속도, 다중 창 경보(1시간·5분 14.4배, 6시간·30분 6배) |
| `demo.py` | `1` 평범한 한 달, `2` 17일 14:00 결제 장애 25분(예산의 40%)과 경보 |
| `solutions/ticket.py` | 연습 풀이: 셋째 줄(3일·6시간·1배 → 티켓)로 천천히 새는 문제 잡기 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
```

## 가정

- 요청 하나하나 대신 분 단위 합계. 분당 90~110건, 평소 실패 약 0.03%, 4xx 분당 약 2건(유효 요청에서 뺌).
- 장애 25분 동안 결제 요청 68% 실패는 지어낸 숫자(예산의 40%가 되게 고름).
- 경보 기준표는 Google SRE Workbook 「Alerting on SLOs」의 권장 표(30일 창 기준)를 따른다: https://sre.google/workbook/alerting-on-slos/
