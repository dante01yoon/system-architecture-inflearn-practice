"""정해 둔 씨앗으로 만드는 서점 주문 흐름: (초, 책 번호). 실행마다 같다."""
import random

BOOKS = 50_000


def purchases(n=200_000, minutes=90, seed=7):
    """책 인기는 앞 번호일수록 높다(지프 분포). 60분부터 신간 「책99999」이 주문의 30%를 차지한다."""
    rnd = random.Random(seed)
    books = [f"책{r:05d}" for r in range(1, BOOKS + 1)]
    picks = rnd.choices(books, cum_weights=_cum(), k=n)
    out = []
    for i, book in enumerate(picks):
        t = i * minutes * 60 / n
        if t >= 60 * 60 and rnd.random() < 0.3:
            book = "책99999"
        out.append((t, book))
    return out


def _cum():
    total, cum = 0.0, []
    for r in range(1, BOOKS + 1):
        total += 1 / r ** 1.1
        cum.append(total)
    return cum
