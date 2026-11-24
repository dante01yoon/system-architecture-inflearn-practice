# deprule — 의존성 규칙: 안쪽은 바깥을 모른다

서점 주문 유스케이스를 동심원 넷으로 나눴다: `bookshop/entities.py`(업무 규칙) ← `bookshop/usecases.py`(PlaceOrder, 저장소 약속 BookRepository Protocol, 경계를 넘는 OrderRequest·OrderResult) ← `bookshop/adapters/`(메모리·SQLite 저장소) ← `bookshop/main.py`(부품 끼우기). `checker.py`는 ast로 import를 읽어 안쪽 원이 바깥 원을 import하면 실패한다. 표준 라이브러리만 쓴다.

    python3 demo.py
    python3 checker.py
    python3 -m unittest
    python3 solutions/json_repo.py   # 연습 문제 풀이(JSON 파일 저장소)
