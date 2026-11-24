# sdi-kv — Dynamo 방식 Key-Value 저장소(파이썬 표준 라이브러리만)

노드 5대를 한 프로세스 안에 두고, 해시 고리(가상 노드 8개씩)로 키의 자리를 정해 N=3개 노드에 복제한다.
쓰기는 W개, 읽기는 R개 응답이면 성공이다. 앞쪽 N개 중 꺼진 노드의 몫은 다음 건강한 노드가 힌트와 함께 맡았다가
그 노드가 돌아오면 넘긴다(sloppy quorum + hinted handoff). 버전마다 벡터 시계를 붙여 동시 쓰기를 알아채고,
Merkle 트리로 두 복제본의 다른 키 구간만 찾는다.

| 파일 | 역할 |
|---|---|
| `kv.py` | `Cluster`(고리 · `put` · `get` · `recover`), `Node.store`(옛 버전 버리기 · 동시 버전 함께 두기), `descends`·`merge`(벡터 시계), `tree`·`diff`(Merkle) |
| `demo.py` | `1` 노드 하나가 꺼졌을 때: 힌트 → 복구 → 힌트를 잃었다면 Merkle, `2` 두 손님이 동시에 쓰면: 벡터 시계 충돌 → 앱이 합침 · LWW와 비교 |
| `solutions/read_repair.py` | 연습 풀이: 읽을 때 옛 복제본 고치기 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
```

노드 이름 · 키 · 가상 노드 수 · 두 서버의 시각 차(5ms)는 설명을 위한 가정이다. 숫자는 이 예제를 돌린 값이다.

## 연습 문제
읽을 때 옛 버전을 들고 있던 복제본을 찾아 고쳐 두는 읽기 복구를 `get`에 붙여 보세요. 풀이: `solutions/read_repair.py`
