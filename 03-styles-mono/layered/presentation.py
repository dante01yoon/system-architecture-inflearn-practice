"""프레젠테이션 층: 요청을 받아 비즈니스 층만 부른다."""
from layered import business


def get_books():
    return business.list_books()


def post_order(req):
    return business.place_order(req)
