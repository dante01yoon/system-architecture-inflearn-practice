import asyncio
import unittest

from chat import Chat, Client, ConnServer


def setup(*names, conv="dm"):
    chat = Chat()
    a, b = ConnServer("A", chat), ConnServer("B", chat)
    users = {n: Client(n) for n in names}
    chat.members[conv] = set(names)
    return chat, a, b, users


class ChatTest(unittest.TestCase):
    def test_routes_to_other_server(self):
        async def run():
            chat, a, b, u = setup("alice", "bob")
            await a.connect(u["alice"]); await b.connect(u["bob"])
            await chat.send("alice", "dm", "hi", "c1")
            return u["bob"].screen
        self.assertEqual([m["text"] for m in asyncio.run(run())], ["hi"])

    def test_offline_inbox_in_order_after_reconnect(self):
        async def run():
            chat, a, b, u = setup("alice", "bob")
            await a.connect(u["alice"])
            for i in range(3):
                await chat.send("alice", "dm", f"m{i}", f"c{i}")
            self.assertEqual(len(chat.pushes), 3)
            await b.connect(u["bob"])
            return [m["id"] for m in u["bob"].screen]
        self.assertEqual(asyncio.run(run()), [1, 2, 3])

    def test_lost_ack_redelivers_but_client_dedups(self):
        async def run():
            chat, a, b, u = setup("alice", "bob")
            await a.connect(u["alice"]); await b.connect(u["bob"])
            u["bob"].lose_acks = 2
            _, sent = await chat.send("alice", "dm", "hi", "c1")
            return sent, u["bob"]
        sent, bob = asyncio.run(run())
        self.assertIn("3번", sent[0][1])
        self.assertEqual((len(bob.screen), bob.dropped), (1, 2))

    def test_sender_retry_same_client_id_stored_once(self):
        async def run():
            chat, a, b, u = setup("alice", "bob")
            await a.connect(u["alice"]); await b.connect(u["bob"])
            m1, _ = await chat.send("alice", "dm", "hi", "c1")
            m2, sent = await chat.send("alice", "dm", "hi", "c1")
            return m1, m2, sent, chat
        m1, m2, sent, chat = asyncio.run(run())
        self.assertIs(m1, m2)
        self.assertEqual((sent, len(chat.history("dm"))), ([], 1))

    def test_disconnect_from_old_server_keeps_new_registration(self):
        async def run():
            chat, a, b, u = setup("bob")
            await a.connect(u["bob"]); await b.connect(u["bob"])
            a.disconnect("bob")
            return chat.registry.find("bob")
        self.assertEqual(asyncio.run(run()).name, "B")

    def test_presence_timeout(self):
        chat = Chat(timeout=15)
        chat.beat("bob", 10)
        self.assertTrue(chat.online("bob", 25))
        self.assertFalse(chat.online("bob", 26))
        self.assertFalse(chat.online("carol", 0))


if __name__ == "__main__":
    unittest.main()
