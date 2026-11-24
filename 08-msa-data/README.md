# msa-data — 서비스마다 자기 데이터, 동기 대 비동기

주문 서비스(`order.py`, `data/orders.db`)와 재고 서비스(`stock.py`, `data/stock.db`)가 각자 자기 sqlite 파일만 연다. 재고 서비스를 끈 채로 (1) 주문이 재고를 바로 부르는 동기 방식과 (2) 주문이 같은 트랜잭션 안에서 아웃박스 표에 쪽지를 남기고 나중에 전달하는 비동기 방식을 비교한다. 파이썬 표준 라이브러리만 쓴다. `demo.py`는 시작할 때 `data/*.db`를 지우고 새로 만든다.

    python3 demo.py
    python3 -m unittest
    python3 solutions/order_view.py   # 연습 문제 풀이(API 조합)
