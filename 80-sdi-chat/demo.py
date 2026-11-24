"""python3 demo.py 1 → 다른 서버 · 오프라인 보관함,  2 → 재시도와 중복 거르기,  3 → 하트비트 접속 표시"""
import asyncio
import sys

from chat import Chat, Client, ConnServer


def show(c):
    return " · ".join(f"#{m['id']} {m['text']}" for m in c.screen)


async def offline():
    chat = Chat()
    a, b = ConnServer("A", chat), ConnServer("B", chat)
    alice, bob = Client("alice"), Client("bob")
    chat.members["dm:alice-bob"] = {"alice", "bob"}
    await a.connect(alice); await b.connect(bob)
    print("1) alice → 서버 A · bob → 서버 B에 연결 (기록부에 적음)")
    msg, sent = await chat.send("alice", "dm:alice-bob", "안녕", "c1")
    print(f"2) alice → bob \"안녕\" · 저장소에 #{msg['id']}")
    print(f"   기록부: bob은 서버 B · {sent[0][1]}")
    print(f"   bob 화면: {show(bob)}")
    b.disconnect("bob")
    print("3) bob 연결 끊김 → 기록부에서 지움")
    print("4) bob이 없는 동안 alice가 두 개 더 보냄")
    for cid, text in (("c2", "책 샀어?"), ("c3", "DDIA 2판")):
        msg, sent = await chat.send("alice", "dm:alice-bob", text, cid)
        print(f"   #{msg['id']} \"{text}\" → {sent[0][1]}")
    print(f"   푸시 알림 {len(chat.pushes)}개 · 보관함 {len(chat.inbox['bob'])}개")
    n = await a.connect(bob)
    print(f"5) bob 다시 연결(이번엔 서버 A) → 보관함 {n}개를 번호 순서대로 받음")
    print(f"   bob 화면: {show(bob)}")
    ids = [m["id"] for m in chat.history("dm:alice-bob")]
    print(f"6) 저장소의 대화 기록 dm:alice-bob → {ids}")


async def retry():
    chat = Chat()
    a, b = ConnServer("A", chat), ConnServer("B", chat)
    alice, bob, carol = Client("alice"), Client("bob"), Client("carol")
    chat.members["g:bookclub"] = {"alice", "bob", "carol"}
    await a.connect(alice); await b.connect(bob); await a.connect(carol)
    print("1) 작은 그룹 g:bookclub · alice와 carol은 서버 A, bob은 서버 B")
    bob.lose_acks = 1
    msg, sent = await chat.send("alice", "g:bookclub", "토요일 3시", "x7")
    print(f"2) alice가 보냄 · 저장 #{msg['id']} · 그룹 두 명에게 fan-out")
    for user, how in sent:
        print(f"   {user:<5} {how}")
    print(f"3) bob은 첫 ack가 사라져서 같은 #{msg['id']}을 두 번 받음")
    print(f"   bob 화면 {len(bob.screen)}개 · 중복 버림 {bob.dropped}개")
    again, sent = await chat.send("alice", "g:bookclub", "토요일 3시", "x7")
    print("4) alice도 응답을 못 받아 다시 보냄 (같은 client_id x7)")
    print(f"   저장소는 같은 #{again['id']}을 돌려줌 · 새 전달 {len(sent)}건")
    print(f"5) 저장된 메시지 {len(chat.history('g:bookclub'))}개 · carol 화면 {len(carol.screen)}개 · bob 화면 {len(bob.screen)}개")


def presence():
    chat = Chat(timeout=15)
    print("1) 하트비트 5초마다 · 15초 동안 없으면 오프라인")
    for t in (0, 5, 10):
        chat.beat("bob", t)
    print("   bob 하트비트: 0초 · 5초 · 10초, 그 뒤로 끊김")
    print("2) 시각별 bob 상태")
    for t in (12, 20, 25, 26, 30):
        print(f"   {t:>2}초  {'온라인' if chat.online('bob', t) else '오프라인'}")
    chat.beat("bob", 31)
    print(f"3) 31초에 하트비트가 다시 옴 → {'온라인' if chat.online('bob', 31) else '오프라인'}")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "1"
    if arg == "3":
        presence()
    else:
        asyncio.run({"1": offline, "2": retry}[arg]())
