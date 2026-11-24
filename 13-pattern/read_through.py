"""Read-Through(데코레이터로 흉내): 부르는 쪽은 캐시를 모른다."""


def read_through(ttl, clock):
    def wrap(load):
        cache = {}

        def get(key):
            hit = cache.get(key)
            if hit and clock() - hit[1] < ttl:  # TTL 안이면 캐시 값
                return hit[0]
            value = load(key)  # 아니면 원본을 부르고
            cache[key] = (value, clock())  # 받은 시각과 함께 넣는다
            return value

        return get

    return wrap


class Shop:
    def __init__(self, remote, ttl, clock):
        self.remote = remote
        self.price = read_through(ttl, clock)(remote.get)

    def change_price(self, isbn, price):
        self.remote.set(isbn, price)  # 캐시는 이 일을 모른다
