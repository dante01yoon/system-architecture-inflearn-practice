# msa-bounds — 바운디드 컨텍스트와 애그리거트

같은 ISBN의 책을 카탈로그(`catalog.Book`)·주문(`ordering.OrderLine`)·배송(`shipping.Parcel`)이 각자 다른 모양으로 들고, `translate.py`가 그 사이를 번역한다. 주문 애그리거트(`ordering.Order`)는 루트로만 바뀌고 「한 주문 10권까지」「합계 0원 이상」을 지킨다. 파이썬 표준 라이브러리만 쓴다.

    python3 demo.py
    python3 -m unittest
    python3 solutions/gift_wrap.py   # 연습 문제 풀이
