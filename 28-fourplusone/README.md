# fourplusone — 4+1 뷰로 서점 그리기

Kruchten의 4+1 뷰 모델(IEEE Software, 1995)대로 서점 하나를 논리·프로세스·개발·물리 뷰로 적고(`bookshop.py`의 dict 하나), +1인 시나리오 「책 주문하기」로 네 뷰가 서로 맞는지 확인한다. 파이썬 표준 라이브러리만 쓴다.

| 파일 | 역할 |
|---|---|
| `bookshop.py` | 모델(뷰 넷)과 시나리오 |
| `fourplusone.py` | 뷰를 글자로 찍기(show), 시나리오 걸어 보기(walk) |
| `demo.py` | 뷰 넷 + 시나리오 검사(일부러 넣은 불일치 하나) + 고친 뒤 |

    python3 demo.py
    python3 -m unittest
    python3 solutions/check.py   # 연습 문제 풀이

## 연습 문제

「주문 취소하기」 시나리오(취소 요청 → 환불하기)를 하나 더 적어 보세요. 환불은 어느 클래스·프로세스·모듈이 맡을까요? walk가 찾아낸 불일치를 모델 쪽에서 고쳐 0건으로 만들어 보세요.
