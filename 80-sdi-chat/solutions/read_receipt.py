"""연습 풀이: 읽음 표시. 사용자마다 대화별 「여기까지 읽음」 번호 하나만 저장한다(메시지마다 표시하지 않는다)."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from chat import Chat, Client, ConnServer  # noqa: E402


class ReadChat(Chat):
    def __init__(self):
        super().__init__()
        self.read_upto = {}                          # (대화, 사용자) → 마지막으로 읽은 번호

    def mark_read(self, conv, user, mid):
        key = (conv, user)
        self.read_upto[key] = max(self.read_upto.get(key, 0), mid)   # 늦게 온 작은 번호로 되돌리지 않는다

    def readers(self, conv, mid, sender):
        return sorted(u for u in self.members[conv] - {sender} if self.read_upto.get((conv, u), 0) >= mid)


async def main():
    chat = ReadChat()
    a = ConnServer("A", chat)
    for n in ("alice", "bob", "carol"):
        await a.connect(Client(n))
    chat.members["g"] = {"alice", "bob", "carol"}
    m1, _ = await chat.send("alice", "g", "토요일?", "r1")
    m2, _ = await chat.send("alice", "g", "3시", "r2")
    chat.mark_read("g", "bob", m2["id"])
    chat.mark_read("g", "carol", m1["id"])
    chat.mark_read("g", "carol", 0)
    for m in (m1, m2):
        print(f"#{m['id']} {m['text']:<5} 읽음 {len(chat.readers('g', m['id'], 'alice'))}/2 {chat.readers('g', m['id'], 'alice')}")
    assert chat.readers("g", m1["id"], "alice") == ["bob", "carol"]
    assert chat.readers("g", m2["id"], "alice") == ["bob"]


if __name__ == "__main__":
    asyncio.run(main())
