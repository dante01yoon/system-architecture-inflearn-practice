shelf = {"Clean Architecture": 3}


def reserve(book, qty):
    shelf[book] -= qty
    return shelf[book]


def release(book, qty):
    shelf[book] += qty
