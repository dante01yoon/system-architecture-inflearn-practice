# kafka-like — Kafka는 왜 이렇게 설계됐나: 장난감 파티션 로그 (파이썬 표준 라이브러리만)

| 파일 | 역할 |
|---|---|
| `klog.py` | `Topic`(키 → 파티션, 파티션마다 덧붙이기만 하는 세그먼트 파일, 컴팩션), `Group`(컨슈머 그룹: 파티션 하나는 한 컨슈머에게, 오프셋 커밋, 재조정) |
| `demo.py` | `1` 주문 이벤트 12건과 컨슈머 둘, `2` 셋째·넷째 컨슈머 합류(재조정), `3` 로그 컴팩션 |
| `solutions/two_groups.py` | 연습 풀이: 같은 토픽을 그룹 둘이 따로 읽기 |

```bash
python3 demo.py 1
python3 demo.py 2
python3 demo.py 3
python3 -m unittest
```

## 진짜 Kafka와 다른 점

- 파티셔너: Kafka 기본은 murmur2 해시, 여기는 `zlib.crc32`.
- 세그먼트: Kafka는 크기·시간으로 자른다(`segment.bytes` 등), 여기는 레코드 4건마다.
- 오프셋 커밋: Kafka는 브로커의 내부 토픽에 저장, 여기는 `Group.committed` 딕셔너리.
- 재조정: 돌아가며 나누기(RoundRobin 방식) 하나만. 복제·배치·압축·sendfile은 없다(영상에서 그림으로 설명).
