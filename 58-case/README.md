# case — 공개 장애 보고서 읽기: AWS DynamoDB DNS 장애(us-east-1, 2025-10-19~20)

AWS가 공개한 사후 보고서(https://aws.amazon.com/message/101925/)의 두 가지 메커니즘을 파이썬 표준 라이브러리로 작게 흉내 낸다.
실제 시스템 이름(DNS Planner · DNS Enactor · DWFM)의 구조만 빌렸고, 세대 번호 · 주소 · 서버 수 · 처리량 · 타임아웃 숫자는 설명을 위한 가정이다.

| 파일 | 역할 |
|---|---|
| `dns.py` | `Zone`(계획 보관함 + 레코드) · `Enactor`(시작할 때만 비교 → 늦은 적용이 새 계획을 덮음, 정리가 쓰던 계획을 지우면 빈 레코드). `safe=True`는 고친 뒤 |
| `storm.py` | `lease_storm`: 복구 뒤 서버들이 한꺼번에 리스를 다시 요청 → 타임아웃 · 재요청이 쌓여 혼잡 붕괴. `limit`을 주면 줄 길이로 조절 |
| `demo.py` | `1` DNS 경쟁 상태(고치기 전 · 뒤), `2` 리스 몰림과 조절(고치기 전 · 뒤) |
| `solutions/skip_stale.py` | 연습 문제 풀이 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
```

## 연습 문제

`storm.py`는 보낸 쪽이 이미 포기한 요청도 한 칸의 일로 처리합니다. 조절(`limit`) 없이, 기한이 지난 요청은 처리하지 않고 버리게 고치면 붕괴가 풀릴까요?
풀이: `python3 solutions/skip_stale.py`
