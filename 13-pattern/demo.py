"""느린 가격 조회 하나를 두 패턴으로 풀고, 패턴마다 결과(consequences)를 센다."""
import cache_aside
import read_through
from price_service import COST_MS, PriceService

CLEAN, DDIA = "Clean Architecture", "DDIA"
PRICES = {CLEAN: 32000, DDIA: 45000}
VIEWS, CHANGE_AT = 20, 5


def run(make):
    """화면 20번, 6번째 화면 직전에 할인. (원격 호출 수, 옛 가격 수)"""
    remote, now = PriceService(PRICES), [0]
    shop = make(remote, lambda: now[0])
    stale = 0
    for t in range(VIEWS):
        now[0] = t
        if t == CHANGE_AT:
            shop.change_price(CLEAN, 28000)
        book = CLEAN if t % 2 == 0 else DDIA
        stale += shop.price(book) != remote.prices[book]
    return remote.calls, stale


class NoCache:
    def __init__(self, remote, clock):
        self.remote = remote
        self.price, self.change_price = remote.get, remote.set


def show(name, calls, stale):
    print(f"   {name}원격 호출 {calls:2}번 · 기다림 {calls * COST_MS / 1000:.1f}초 · 옛 가격 {stale}번")


def main():
    print(f"문제: 가격 조회 한 번에 {COST_MS}ms (화면 {VIEWS}번, 6번째 화면부터 할인가)")
    print("1) 패턴 없이: 화면마다 원격 호출")
    show("", *run(NoCache))
    print("2) cache-aside: 부르는 쪽이 캐시를 챙긴다")
    show("", *run(lambda r, c: cache_aside.Shop(r)))
    show("지우기 깜빡: ", *run(lambda r, c: cache_aside.Shop(r, forget=True)))
    print("3) read-through: 데코레이터가 캐시를 숨긴다")
    for ttl in (10, 4):
        show(f"TTL {ttl:2}: ", *run(lambda r, c: read_through.Shop(r, ttl, c)))
    print("4) 결과(consequences)")
    print("   cache-aside : 옛 가격 0 / 대가: 값을 바꾸는 곳마다 캐시 지우기")
    print("   read-through: 부르는 코드는 그대로 / 대가: TTL만큼 옛 가격")


if __name__ == "__main__":
    main()
