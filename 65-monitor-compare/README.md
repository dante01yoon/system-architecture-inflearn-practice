# 모니터링 셋 비교 예제: 같은 장애를 세 방법으로 (파이썬 표준 라이브러리만)

서점 20분치 분 단위 숫자를 가정해 둔다(`incident.py`). 8분째부터 외부 결제 API가 느려지고, `/checkout`이 DB 연결을 쥔 채 기다려서 연결 풀이 찬다(USE·RED 수업과 같은 장애).
같은 숫자를 네 가지 신호 · RED · USE · SLO 소진 속도로 읽는다(`methods.py`).

| 파일 | 역할 |
|---|---|
| `incident.py` | `minutes()` 분마다 서비스(R·E·D)·자원(U·S·E)·1초 넘은 요청 % (가정한 값) |
| `methods.py` | `golden`(서비스 하나의 네 가지 신호) · `red`(서비스마다) · `use`(자원마다) · `burn`(최근 5분 오류율 ÷ 예산) |
| `demo.py` | `1` 분마다 세 방법이 표시한 것, `2` SLO 호출 → RED → USE → 트레이스 → 원인 |
| `solutions/latency_slo.py` | 연습 문제 풀이 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
```

경보 규칙은 줄였다: SRE 실습서 표의 첫 줄(14.4배)만, 창은 5분 하나(실제로는 1시간 창과 함께 본다).

## 연습 문제

지연 SLO(요청의 99%가 1초 안에)를 더하면 호출이 몇 분에 울리는지 계산해 보세요(`LOG[t]["slow"]` = 1초 넘은 요청 %).
풀이: `python3 solutions/latency_slo.py`
