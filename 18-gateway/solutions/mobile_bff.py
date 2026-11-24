"""연습 풀이: 모바일 앱 전용 BFF. 게이트웨이의 책 화면을 받아 작은 화면에 필요한 세 칸만 남긴다(업무 규칙은 넣지 않는다)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gateway  # noqa: E402
import services  # noqa: E402


def mobile_book_page(isbn):
    page = gateway.book_page(isbn)
    stars = page["reviews"]["stars"] if page["reviews"] else None  # 리뷰가 꺼져도 화면은 나온다
    return {"title": page["catalog"]["title"], "price": page["catalog"]["price"], "stars": stars}


if __name__ == "__main__":
    servers = [services.start(n) for n in services.PORTS]
    print(mobile_book_page("9780134494166"))
    for s in servers:
        s.shutdown()
