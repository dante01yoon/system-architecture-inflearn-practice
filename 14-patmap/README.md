# patmap — 증상에서 출발해 패턴 찾기

`patmap.py`는 증상 한 줄에서 패턴 지도(`MAP`, 칸 여덟 개)의 낱말을 찾아, 가장 많이 맞는 패턴과 그 문제·대가·배울 수업을 출력한다. 낱말 맞추기라서 지도를 고르는 판단은 사람이 한다. 파이썬 표준 라이브러리만 쓴다.

    python3 patmap.py "추천 서비스가 느려지면 주문까지 멈춰요"
    python3 demo.py        # 서점 증상 네 개
    python3 -m unittest
    python3 solutions/add_retry.py   # 연습 문제 풀이(Retry 칸 추가)
