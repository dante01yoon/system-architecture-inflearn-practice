"""연습 풀이: 파이프라이닝 — INCR 1000개를 답을 기다리지 않고 한꺼번에 보낸 뒤 답을 모아 읽는다.
python3 solutions/pipeline.py   (server.py를 8896에 잠깐 띄운다)"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from client import Client  # noqa: E402

PORT, N = 8896, 1000
srv = subprocess.Popen([sys.executable, str(HERE / "server.py"), str(PORT)])
try:
    c = Client(PORT)
    t = time.perf_counter()
    for _ in range(N):
        c.cmd("INCR one")                             # 하나 보내고 답을 기다리기를 N번
    one = time.perf_counter() - t
    t = time.perf_counter()
    c.f.write(b"INCR pipe\n" * N); c.f.flush()        # 한꺼번에 보내고
    last = [c.f.readline() for _ in range(N)][-1]     # 답을 모아 읽는다
    pipe = time.perf_counter() - t
    print(f"하나씩 {one * 1000:.0f}ms · 파이프라이닝 {pipe * 1000:.0f}ms · 마지막 답 {last.decode().strip()}")
    assert last.strip() == str(N).encode()
finally:
    srv.terminate(); srv.wait()
