"""입구: 요청을 알맞은 모듈로 보낸다."""
from modular import catalog, ordering


def get_books():
    return catalog.titles()


def post_order(req):
    return ordering.place_order(req)
