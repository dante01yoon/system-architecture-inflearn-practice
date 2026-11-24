# evsrc — 이벤트 소싱: 바뀐 기록을 원본으로

`store.py`는 sqlite3 표 하나에 이벤트를 덧붙이기만 하는 저장소다(책 한 권 = 이벤트 줄 하나, `(stream, version)`이 기본 키라 같은 버전에 두 번 쓰면 `Conflict`). `stock.py`는 이벤트를 차례로 적용해 재고를 만들고(`rebuild`), 스냅숏 뒤 이벤트만 적용하고(`load`), 옛 모양 이벤트를 읽을 때 바꾸고(`upcast`), 같은 이벤트로 날짜별 판매 읽기 모델을 만든다(`sales_by_day`). 표준 라이브러리만 쓴다.

    python3 demo.py
    python3 -m unittest
    python3 solutions/price_change.py   # 연습 문제 풀이(가격 이벤트와 「수요일 가격」)
