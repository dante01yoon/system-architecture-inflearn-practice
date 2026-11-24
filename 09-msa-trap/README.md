# msa-trap — 분산 모놀리스 신호 찾기

서점 서비스 넷(order·catalog·stock·payment)의 배포 기록·동기 호출·DB 설정을 JSON으로 적고, `trap.py`가 분산 모놀리스 신호 세 가지를 찾는다. 파이썬 표준 라이브러리만 쓴다.

| 파일 | 역할 |
|---|---|
| `trap.py` | 늘 같이 배포된 쌍(lockstep), 입구에서 2홉보다 깊은 동기 호출 사슬, 공유 DB |
| `distributed.json` | 지금 서점: 신호 3개 |
| `fixed.json` | 고친 서점: 신호 0개 |
| `demo.py` | 두 설정을 나란히 진단 |

    python3 demo.py
    python3 -m unittest
    python3 solutions/check.py   # 연습 문제 풀이

## 연습 문제

`distributed.json`에서 서비스 넷은 그대로 두고, 설정 두 줄만 바꿔 호출 사슬과 공유 DB 신호를 없애 보세요(힌트: stock이 payment를 직접 부르지 않으면?). 같이 배포 신호는 왜 설정만 바꿔서는 사라지지 않을까요?
