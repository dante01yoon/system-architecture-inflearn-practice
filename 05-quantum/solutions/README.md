# 연습 문제 풀이

문제: shop.txt에 `sync review catalog`(리뷰 화면이 책 정보를 동기 호출로 받음)를 한 줄 더하면 퀀텀이 몇 개가 될까?

풀이: review가 catalog에 묶이고, catalog는 shop_db로 stock에, stock은 order 호출로 order 무리에 묶여 있다.
그래서 서비스 6개가 모두 퀀텀 1개가 된다. `python3 solutions/check.py`로 확인.
