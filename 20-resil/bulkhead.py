"""벌크헤드: 부르는 상대마다 일꾼 묶음(스레드 풀)을 따로 둔다."""
from concurrent.futures import ThreadPoolExecutor, wait


def shared_pool(workers):
    pool = ThreadPoolExecutor(workers)
    return {"review": pool, "order": pool}  # 리뷰도 주문도 같은 일꾼을 나눠 쓴다


def bulkheads(sizes):
    return {name: ThreadPoolExecutor(n) for name, n in sizes.items()}


def call_with_timeout(future, seconds, fallback):
    done, _ = wait([future], timeout=seconds)
    if done:
        return future.result()
    return fallback  # 기다림만 끝낸다. 일꾼은 답이 올 때까지 여전히 붙잡혀 있다
