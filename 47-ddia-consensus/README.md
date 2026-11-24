# ddia-consensus — 선형성, 2단계 커밋, 과반 선거

서점 재고로 선형성 검사, 2단계 커밋(2PC)에서 코디네이터가 멈추는 상황, 5대가 3|2로 갈라졌을 때의 과반 선거를 흉내 낸다. 시간은 밀리초 숫자이고 숫자는 설명을 위한 가정이다. 선거는 Raft(Ongaro · Ousterhout, USENIX ATC 2014)의 「임기마다 한 표 · 과반」만 줄인 모양이고, 로그 비교·타임아웃 같은 나머지 규칙은 뺐다. 파이썬 표준 라이브러리만 쓴다.

| 파일 | 역할 |
|---|---|
| `linear.py` | `check`: 실제 시간 순서를 지키는 한 줄 순서가 있는지 모든 순서를 본다(기록이 작을 때만) |
| `twopc.py` | `Coordinator`(준비 → 결정을 로그에 → 알림) · `Participant`(예라고 답하면 잠금을 쥐고 기다림) |
| `election.py` | `Node.vote`(임기마다 한 표) · `elect`(닿는 노드에서 과반이면 리더) |
| `demo.py` | `1` 선형성, `2` 2PC 코디네이터 멈춤, `3` 3|2 갈라짐 선거 |
| `solutions/even_split.py` | 연습 문제 풀이 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 demo.py 3
python3 -m unittest
```

## 연습 문제

노드를 4대로 두고 2|2로 갈라 보세요. 어느 쪽에서 리더가 생기나요? 5대일 때와 견딜 수 있는 고장 수를 비교해 보세요.
풀이: `python3 solutions/even_split.py`
