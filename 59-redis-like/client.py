"""한 줄 명령을 보내고 한 줄 답을 받는 작은 손님."""
import socket
import time

PORT = 8899


class Client:
    def __init__(self, port=PORT):
        for _ in range(100):                         # 서버가 막 뜨는 중이면 조금 기다린다
            try:
                self.sock = socket.create_connection(("127.0.0.1", port))
                break
            except ConnectionRefusedError:
                time.sleep(0.05)
        else:
            raise RuntimeError(f"127.0.0.1:{port}에 서버가 없음")
        self.f = self.sock.makefile("rwb")

    def cmd(self, line):
        self.f.write((line + "\n").encode()); self.f.flush()
        return self.f.readline().decode().strip()

    def close(self):
        self.f.close(); self.sock.close()
