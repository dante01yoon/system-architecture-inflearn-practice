"""책 화면 하나를 그리는 데 모바일 앱이 몇 번 왕복하나: 게이트웨이 없이 / 있을 때."""
import time
from urllib.request import Request, urlopen

import gateway
import services
from client import App

ISBN = "9780134494166"


def avg_ms(url, n=200):
    req, t0 = Request(url, headers={"Authorization": gateway.TOKEN}), time.perf_counter()
    for _ in range(n):
        urlopen(req).read()
    return (time.perf_counter() - t0) / n * 1000


def main():
    servers = [services.start(n) for n in services.PORTS] + [gateway.start()]

    print("1) 게이트웨이 없이: 앱이 서비스 셋을 직접 부른다")
    app, t0 = App(), time.perf_counter()
    for name, port in services.PORTS.items():
        status, body = app.get(port, f"/{name}/{ISBN}")
        print(f"   {port} /{name} -> {body}")
    print(f"   왕복 {app.trips}번, {time.perf_counter() - t0:.2f}초")

    print("2) 게이트웨이로: 문 하나에 한 번만")
    app, t0 = App(gateway.TOKEN), time.perf_counter()
    status, page = app.get(8814, f"/book-page/{ISBN}")
    print(f"   8814 /book-page -> {' + '.join(page)} 한 번에")
    print(f"   왕복 {app.trips}번, {time.perf_counter() - t0:.2f}초")

    print("3) 토큰 없이 게이트웨이에")
    status, body = App().get(8814, f"/book-page/{ISBN}")
    print(f"   {status} {body['error']} (서비스까지 가지 않음)")

    print("4) 한 칸 더 거치는 값 (모바일 망 빼고, 200번 평균)")
    print(f"   카탈로그 직접 {avg_ms(f'http://127.0.0.1:8811/catalog/{ISBN}'):.2f}ms")
    print(f"   게이트웨이 거쳐 {avg_ms(f'http://127.0.0.1:8814/catalog/{ISBN}'):.2f}ms")

    print("5) 리뷰 서비스가 꺼지면")
    servers.pop(1).shutdown()
    status, page = App(gateway.TOKEN).get(8814, f"/book-page/{ISBN}")
    print(f"   reviews={page['reviews']}, 제목·재고는 그대로: {page['catalog']['title']}, {page['stock']['left']}권")

    for s in servers:
        s.shutdown()


if __name__ == "__main__":
    main()
