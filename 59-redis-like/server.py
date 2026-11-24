"""스레드 하나짜리 이벤트 루프 키-값 서버(Redis 흉내). selectors가 운영체제에 맞는 epoll · kqueue를 고른다.
python3 server.py [포트]   — 기본 8899, 127.0.0.1에서만 받는다. 한 줄에 명령 하나, 답도 한 줄."""
import selectors
import socket
import sys
from fnmatch import fnmatchcase

DB, ORDER = {}, []   # shortcut: 키를 지우지 않아서 SCAN 커서 = ORDER 번호. 지우기를 넣으면 Redis처럼 해시 테이블 커서로


def run(line):
    op, *a = line.split()
    if op == "INCR":
        if a[0] not in DB:
            ORDER.append(a[0])
        DB[a[0]] = int(DB.get(a[0], 0)) + 1
        return str(DB[a[0]])
    if op == "GET":
        return str(DB.get(a[0], "(nil)"))
    if op == "FILL":                                 # 시험용: user:0 … user:N-1
        for i in range(int(a[0])):
            DB[f"user:{i}"] = i
            ORDER.append(f"user:{i}")
        return "OK"
    if op == "KEYS":
        return str(sum(1 for k in DB if fnmatchcase(k, a[0])))
    if op == "SCAN":
        c, n = int(a[0]), int(a[1])
        hit = sum(1 for k in ORDER[c:c + n] if fnmatchcase(k, a[2]))
        return f"{c + n if c + n < len(ORDER) else 0} {hit}"
    return "ERR unknown command"


def serve(port):
    sel = selectors.DefaultSelector()
    lsock = socket.create_server(("127.0.0.1", port))
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ)
    buf = {}
    while True:
        for key, _ in sel.select():
            s = key.fileobj
            if s is lsock:
                conn, _ = lsock.accept()
                conn.setblocking(False)
                sel.register(conn, selectors.EVENT_READ)
                buf[conn] = b""
                continue
            data = s.recv(65536)
            if not data:                             # 손님이 연결을 닫음
                sel.unregister(s); s.close(); buf.pop(s)
                continue
            buf[s] += data
            while b"\n" in buf[s]:
                line, buf[s] = buf[s].split(b"\n", 1)
                s.sendall((run(line.decode()) + "\n").encode())  # shortcut: 짧은 답만, 큰 답은 쓰기 이벤트로


if __name__ == "__main__":
    serve(int(sys.argv[1]) if len(sys.argv) > 1 else 8899)
