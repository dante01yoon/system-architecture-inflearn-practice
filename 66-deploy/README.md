# 무중단 배포 예제: 롤링 카나리와 expand-and-contract (파이썬 표준 라이브러리만)

| 파일 | 역할 |
|---|---|
| `canary.py` | 인스턴스 20대를 v1 → v2로 1 · 5 · 10 · 20대씩 바꾸며 단계마다 10분 지켜보기, v2 몫의 소진 속도가 14.4배를 넘으면 되돌림 (요청·오류는 seed 고정 가정) |
| `migrate.py` | sqlite3 `books.price` → `price_krw` 이름 바꾸기 6단계(늘리기 → 두 칸 쓰기 → 채우기 → 읽기 바꾸기 → 옛 칸 쓰기 멈춤 → 줄이기), 단계마다 옛 앱과 새 앱이 함께 쓰고 읽는다 |
| `demo.py` | `1` 정상판·버그판 카나리, `2` 한 번에 이름 바꾸기 대 6단계 |
| `solutions/small_bug.py` | 연습 문제 풀이 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
```

sqlite 3.35 이상이 필요하다(`DROP COLUMN`).

## 연습 문제

v2 버그가 100건 중 1건만 실패시키면(`rollout(0.01)`) 5% 카나리가 잡아낼까요? 씨앗을 바꿔 가며 세어 보고, 잡히게 하려면 기준과 지켜보는 시간을 어떻게 바꿀지 생각해 보세요.
풀이: `python3 solutions/small_bug.py`
