"""서점 서버 하나로 벌크헤드 · 타임아웃 · 재시도 몰림 · 멱등성 키를 차례로 본다."""
import random
import time

from bulkhead import bulkheads, call_with_timeout, shared_pool
from payment import PaymentServer
from retry import retry
from services import Review, place_order
from storm import simulate

FALLBACK = "리뷰를 잠시 불러올 수 없어요"


def order_wait(pools, review):
    for _ in range(8):  # 책 화면 손님 8명이 먼저 와서 리뷰를 부른다
        pools["review"].submit(review.get)
    start = time.time()
    pools["order"].submit(place_order, 1).result()
    return time.time() - start


def main():
    review = Review()
    review.slow = True
    print("1) 칸막이 없이: 일꾼 4명을 리뷰와 주문이 나눠 씀, 리뷰가 1초씩 느려짐")
    print(f"   주문 하나가 기다린 시간 {order_wait(shared_pool(4), review):.1f}초")
    print("2) 벌크헤드: 리뷰 일꾼 2명, 주문 일꾼 2명 따로")
    pools = bulkheads({"review": 2, "order": 2})
    print(f"   주문 하나가 기다린 시간 {order_wait(pools, review):.1f}초")
    print("3) 타임아웃 0.3초: 책 화면은 리뷰를 0.3초까지만 기다림")
    pools = bulkheads({"review": 2, "order": 2})
    start = time.time()
    text = call_with_timeout(pools["review"].submit(review.get), 0.3, FALLBACK)
    print(f"   {time.time() - start:.1f}초 만에 응답: {text}")

    print("4) 손님 100명이 동시에 실패한 뒤 다시 시도 (서버는 0.5초에 30건까지)")
    for name, jitter in [("백오프만", False), ("백오프 + 지터", True)]:
        top, calls, done = simulate(jitter)
        print(f"   {name}: 0.5초에 최대 {top}건 · 요청 {calls}건 · {done:.1f}초에 끝남")

    for step, key in [("5) 키 없이", None), ("6) 멱등성 키와 함께", "order-7-pay")]:
        server = PaymentServer()
        server.lose_reply = 1  # 첫 결제의 응답이 돌아오는 길에 끊긴다
        pay = lambda: server.charge("order-7", 18000, key)  # noqa: E731
        reply = retry(pay, 3, random.Random(1), sleep=lambda s: None)  # 기다리는 척만
        n, total = server.total("order-7")
        print(f"{step} 결제 재시도: 응답 결제 #{reply['charge']} · 실제 결제 {n}번 · {total:,}원")


if __name__ == "__main__":
    main()
