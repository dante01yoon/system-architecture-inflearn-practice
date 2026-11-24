# gateway — API 게이트웨이: 문 하나로 모으기

서점 서비스 셋(`services.py`: 카탈로그 8811, 리뷰 8812, 재고 8813)과 게이트웨이(`gateway.py`, 8814)를 한 프로세스 안의 스레드로 띄운다. 게이트웨이는 토큰을 확인하고, 경로 앞부분으로 서비스를 고르고(라우팅), `/book-page/<isbn>`은 세 서비스를 동시에 불러 하나로 합친다(집계). `client.py`는 모바일 앱 흉내로, 요청마다 모바일 망 왕복 0.08초를 더하고 왕복 횟수를 센다. 표준 라이브러리만 쓴다.

    python3 demo.py
    python3 -m unittest
    python3 solutions/mobile_bff.py   # 연습 문제 풀이(모바일 전용 BFF)
