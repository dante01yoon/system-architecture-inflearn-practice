"""채팅 서버를 한 프로세스 안에 작게: 연결 서버 둘 · 위치 기록부 · 저장소 · 오프라인 보관함 · 중복 거르기 · 하트비트."""
import asyncio


class Registry:
    """누가 어느 연결 서버에 붙어 있나(실제로는 여러 서버가 함께 보는 키-값 저장소)."""
    def __init__(self):
        self.where = {}

    def find(self, user):
        return self.where.get(user)


class Store:
    """메시지 저장소: 대화마다 번호를 1씩 올려 순서를 정한다(키 = 대화 id + 메시지 id)."""
    def __init__(self):
        self.rows, self.last, self.by_client = {}, {}, {}

    def append(self, conv, sender, text, client_id):
        if client_id in self.by_client:            # 보낸 쪽 재시도 → 같은 메시지를 돌려준다
            return self.by_client[client_id], False
        mid = self.last[conv] = self.last.get(conv, 0) + 1
        msg = {"conv": conv, "id": mid, "from": sender, "text": text}
        self.rows.setdefault(conv, []).append(msg)
        self.by_client[client_id] = msg
        return msg, True


class Client:
    """사용자 앱. 받은 (대화, 번호)를 기억해 두 번 온 메시지는 버린다."""
    def __init__(self, name):
        self.name, self.seen, self.screen, self.dropped = name, set(), [], 0
        self.lose_acks = 0                          # 받고도 ack가 사라지는 횟수(네트워크 흉내)

    def receive(self, msg):
        key = (msg["conv"], msg["id"])
        if key in self.seen:
            self.dropped += 1
        else:
            self.seen.add(key)
            self.screen.append(msg)
        if self.lose_acks:
            self.lose_acks -= 1
            return False
        return True


class ConnServer:
    """WebSocket 연결을 들고 있는 서버(상태가 있다)."""
    def __init__(self, name, chat):
        self.name, self.chat, self.conns = name, chat, {}

    async def connect(self, client):
        self.conns[client.name] = client
        self.chat.registry.where[client.name] = self
        waiting = self.chat.inbox.pop(client.name, [])
        for msg in sorted(waiting, key=lambda m: (m["conv"], m["id"])):
            await self.push(client.name, msg)
        return len(waiting)

    def disconnect(self, user):
        self.conns.pop(user, None)
        if self.chat.registry.find(user) is self:
            del self.chat.registry.where[user]

    async def push(self, user, msg, retry_after=0.01, tries=3):
        """최소 한 번 전달: ack가 없으면 조금 뒤 다시 보낸다."""
        for n in range(1, tries + 1):
            await asyncio.sleep(0)                  # 네트워크 한 번 건너기
            if self.conns[user].receive(msg):
                return n
            await asyncio.sleep(retry_after)
        return tries


class Chat:
    def __init__(self, timeout=15):
        self.registry, self.store, self.inbox, self.pushes = Registry(), Store(), {}, []
        self.members, self.beats, self.timeout = {}, {}, timeout

    async def send(self, sender, conv, text, client_id):
        msg, new = self.store.append(conv, sender, text, client_id)
        sent = []
        if new:
            for user in sorted(self.members[conv] - {sender}):
                sent.append((user, await self.deliver(user, msg)))
        return msg, sent

    async def deliver(self, user, msg):
        srv = self.registry.find(user)
        if srv is None:                             # 오프라인 → 보관함 + 푸시 알림
            self.inbox.setdefault(user, []).append(msg)
            self.pushes.append((user, msg["id"]))
            return "보관함 + 푸시"
        tries = await srv.push(user, msg)
        return f"서버 {srv.name} → {tries}번 보냄"

    def history(self, conv, after=0):
        return [m for m in self.store.rows.get(conv, []) if m["id"] > after]

    # ── 접속 표시: 하트비트 ──
    def beat(self, user, t):
        self.beats[user] = t

    def online(self, user, t):
        return user in self.beats and t - self.beats[user] <= self.timeout
