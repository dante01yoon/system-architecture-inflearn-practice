# 비기능 요구사항 예제: 응답 시간을 숫자로, 그리고 꼬리 지연 (파이썬 표준 라이브러리만)

온라인 서점 주문 API의 응답 시간을 seed 고정으로 1만 개 만들어(대부분 40ms 언저리, 1%는 300~1200ms 멈춤),
평균·중앙값(p50)·p95·p99·p999와 구간별 개수를 본다. 그다음 페이지 하나가 백엔드 N개를 동시에 부를 때
페이지가 느려질 확률(1 - 0.99^N)을 계산과 시뮬레이션으로 비교한다.

응답 시간 분포는 가정이다(로그 정규 + 1% 멈춤). 실제 서비스는 직접 잰 값으로 바꿔 넣는다.

| 파일 | 역할 |
|---|---|
| `latency.py` | `sample`(응답 시간 만들기), `percentile`, `summary`, `histogram`, `page_times`(백엔드 N개 중 가장 늦은 것), `chance_slow` |
| `demo.py` | `1` 분포와 백분위, `2` 꼬리 지연 증폭 |
| `solutions/hedged.py` | 연습 문제 풀이 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
```

## 연습 문제

백엔드 10개 페이지의 p99를 줄여 보세요. 힌트: 한 백엔드가 p95보다 늦으면 같은 요청을 다른 복제본에 한 번 더 보내고 먼저 온 답을 쓴다(Dean·Barroso, The Tail at Scale, 2013의 hedged request).
풀이: `python3 solutions/hedged.py`
