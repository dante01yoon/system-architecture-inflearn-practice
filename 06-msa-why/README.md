# msa-why — 독립 배포 맛보기

catalog(책 값)와 order(주문) 두 서비스를 `http.server`로 띄우고, catalog만 새 버전으로 다시 띄우는 동안 order가 계속 답하는지 본다. 같은 일을 하는 모놀리스와 비교한다. 파이썬 표준 라이브러리만 쓴다. 포트 8701~8703.

    python3 demo.py
    python3 -m unittest
    python3 solutions/check.py   # 연습 문제 풀이
