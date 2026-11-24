"""카탈로그 모듈: 책과 가격. 다른 모듈은 이 파일의 함수만 부른다."""

_BOOKS = {"Clean Architecture": 32000, "Release It!": 28000}


def titles():
    return sorted(_BOOKS)


def price_of(title):
    return _BOOKS[title]
