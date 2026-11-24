# strangler — Strangler Fig: 레거시를 문 뒤에서 조금씩 갈아 끼우기

`legacy.py`는 책 정보·리뷰·주문을 다 하는 오래된 서점 함수 묶음, `newshop.py`는 그 일을 하나씩 옮겨 받는 새 서비스다. `facade.py`의 문(Facade)이 모든 요청을 받아 길 안내표(routes)대로 보낸다. `compare`로 두면 레거시가 답하고 새 서비스 답은 비교만 한다(나란히 돌리기, parallel run). 표준 라이브러리만 쓴다.

    python3 demo.py
    python3 -m unittest
    python3 solutions/move_order.py   # 연습 문제 풀이(order 옮기기)
