# ddia-model — 같은 서점 데이터를 관계형·문서·그래프로

책·저자는 실제 출간 정보(8명 · 8권), 가격·주문 12건은 예제용이다. 파이썬 표준 라이브러리만 쓴다.

| 파일 | 역할 |
|---|---|
| `shop.py` | 데이터 하나(저자 · 책 · 주문) |
| `relational.py` | SQLite 테이블 5개, 번호(ID)로 잇고 조인으로 합친다 |
| `document.py` | 주문·책을 JSON 문서 하나로, 책 제목·저자 이름을 복사해 넣는다 |
| `graph.py` | 노드와 이름 붙은 간선(WROTE, HAS)의 인접 리스트 |
| `demo.py` | 1 = 주문 #7 꺼내기, 2 = 공저자의 다른 책 찾기 · 저자 이름 바꾸기 |

    python3 demo.py 1
    python3 demo.py 2
    python3 -m unittest
    python3 solutions/doc_refs.py   # 연습 문제 풀이

숫자(조인 수, 훑은 문서 수, 따라간 간선 수)는 이 작은 예제에서 센 값이다. 실제 DB는 인덱스·쿼리 최적화기가 일하는 방식을 바꾼다.

## 연습 문제

`document.py`가 저자 이름을 복사하지 않고 저자 번호만 넣게 바꿔 보세요. 이름 바꾸기는 몇 곳을 고치게 되고,
주문 #7을 화면에 보여 주려면 문서를 몇 개 읽어야 하나요? 풀이: `python3 solutions/doc_refs.py`
