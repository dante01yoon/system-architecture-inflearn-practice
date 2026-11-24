# hexa — 헥사고날 아키텍처: 포트와 어댑터

서점 「주문하기」 규칙(`shop/core.py`의 `BookShop`)은 포트(`shop/ports.py`의 Protocol)만 안다. 주도하는 포트(driving) `OrderService`는 바깥이 앱을 부르는 입구, 주도되는 포트(driven) `BookRepository`·`PaymentGateway`·`Notifier`는 앱이 바깥을 부르는 출구다. 어댑터(`adapters/`): CLI·HTTP JSON(입구), SQLite·콘솔 알림·테스트용 가짜(출구). `demo.py`는 같은 육각형을 CLI·HTTP·테스트 세 입구로 부르고, 각각 어떤 어댑터가 끼워졌는지 찍는다. 표준 라이브러리만 쓴다.

    python3 demo.py
    python3 -m unittest
    python3 solutions/batch_csv.py   # 연습 문제 풀이(배치 스크립트 입구)
