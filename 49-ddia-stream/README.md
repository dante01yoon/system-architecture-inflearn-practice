# ddia-stream — 스트림 처리와 CDC: 이중 쓰기 대 변경 로그, 이벤트 시각 창 (파이썬 표준 라이브러리만)

DDIA 2판 12장 「Stream Processing」에서 다루는 주제를 온라인 서점 예제로 돌려 본다.

| 파일 | 역할 |
|---|---|
| `stream.py` | SQLite 주문 테이블 + 트리거로 채우는 변경 로그(CDC 흉내), 이중 쓰기 재현, 변경 로그 소비자(오프셋), 텀블링 윈도(워터마크·기다림) |
| `demo.py` | `1` 두 요청이 동시에 이중 쓰기 → 인덱스가 어긋남, CDC 소비자 → 같음, `2` 도착 시각 대 일어난 시각 1분 창과 늦은 이벤트 |
| `solutions/hopping.py` | 연습 문제 풀이(호핑 윈도) |

```bash
python3 demo.py 1
python3 demo.py 2
python3 -m unittest
```

## 무엇이 진짜이고 무엇이 흉내인가

- 진짜 CDC(예: Debezium)는 데이터베이스의 복제 로그(PostgreSQL WAL의 logical decoding, MySQL binlog)를 읽는다. 여기서는 `changes` 테이블을 트리거가 채운다. 커밋된 변경이 커밋 순서대로 남는다는 성질만 같다.
- 이중 쓰기의 경쟁은 스레드 대신 쓰기 순서를 고정해서 재현한다. 실제로는 네트워크 지연·재시도로 이런 순서가 가끔 생긴다.
- 검색 인덱스·캐시는 파이썬 딕셔너리다.

## 연습 문제

1분 창을 30초마다 새로 여는 호핑 윈도로 같은 판매를 세 보세요. 한 판매가 창 두 개에 들어갑니다.
풀이: `python3 solutions/hopping.py`
