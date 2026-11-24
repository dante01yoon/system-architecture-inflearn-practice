"""python3 demo.py 1 → 스레드 200개의 동시 INCR(잠금 없음),  2 → 느린 KEYS가 GET을 막음 · SCAN은 사이사이 양보
서버(server.py)를 127.0.0.1:8899에 띄웠다가 끝나면 끈다."""
import subprocess
import sys
import threading
import time

from client import PORT, Client

N = 200


def naive_counter():
    """잠금 없는 파이썬 카운터: 모두 읽은 뒤에 쓰도록 맞춰서, 읽고-더하고-쓰기 사이에 끼어드는 순간을 만든다."""
    box, gate = {"n": 0}, threading.Barrier(N)

    def work():
        v = box["n"]                                  # 읽고
        gate.wait()                                   # (모두 같은 값을 읽은 순간)
        box["n"] = v + 1                              # 더하고 쓰기
    ts = [threading.Thread(target=work) for _ in range(N)]
    [t.start() for t in ts]; [t.join() for t in ts]
    return box["n"]


def one():
    n = naive_counter()
    print(f"1. 잠금 없는 파이썬 카운터 · 스레드 {N}개가 읽고-더하고-쓰기")
    print(f"   결과 {n} ({N}이어야 하는데 {N - n}번을 잃어버림)")
    gate = threading.Barrier(N)

    def work():
        c = Client(); gate.wait(); c.cmd("INCR counter"); c.close()   # 모두 동시에 보낸다
    ts = [threading.Thread(target=work) for _ in range(N)]
    [t.start() for t in ts]; [t.join() for t in ts]
    print(f"2. 서버에 스레드 {N}개가 동시에 INCR counter")
    print(f"   GET counter → {Client().cmd('GET counter')} (잠금 없이 정확)")
    print("   서버는 스레드 하나: 명령을 한 줄로 세워 하나씩 끝까지 실행")


def ping(stop, out):
    c = Client()
    while not stop.is_set():
        t = time.perf_counter(); c.cmd("GET counter"); out.append(time.perf_counter() - t)
        time.sleep(0.002)


def worst(job):
    """job을 도는 동안 다른 손님의 GET 최대 지연(ms)과 job이 걸린 시간(ms)."""
    stop, lat = threading.Event(), []
    p = threading.Thread(target=ping, args=(stop, lat)); p.start(); time.sleep(0.1)
    t = time.perf_counter(); r = job(); took = (time.perf_counter() - t) * 1000
    time.sleep(0.05); stop.set(); p.join()
    return r, took, max(lat) * 1000


def scan_all(c):
    cur, n, total = 0, 0, 0
    while True:
        cur, hit = map(int, c.cmd(f"SCAN {cur} 1000 user:*").split())
        n += 1; total += hit
        if cur == 0:
            return n, total


def two():
    c = Client(); c.cmd("FILL 1000000")
    print("1. 키 1,000,000개를 넣음")
    _, _, base = worst(lambda: time.sleep(0.3))
    print(f"2. 평소 GET 최대 지연 {base:.1f}ms")
    r, took, w = worst(lambda: c.cmd("KEYS user:*"))
    print(f"3. KEYS user:* → {int(r):,}개, {took:.0f}ms 동안 한 번에")
    print(f"   그동안 GET 최대 지연 {w:.0f}ms: KEYS가 끝날 때까지 줄 섬")
    (n, total), took, w = worst(lambda: scan_all(c))
    print(f"4. SCAN 1000개씩 {n}번 → {total:,}개, 모두 {took:.0f}ms")
    print(f"   그동안 GET 최대 지연 {w:.1f}ms: 조각 사이에 끼어듦")


if __name__ == "__main__":
    srv = subprocess.Popen([sys.executable, "server.py", str(PORT)])
    try:
        {"1": one, "2": two}[sys.argv[1] if len(sys.argv) > 1 else "1"]()
    finally:
        srv.terminate(); srv.wait()
