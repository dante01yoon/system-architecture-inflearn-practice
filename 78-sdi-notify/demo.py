"""python3 demo.py 1 → 알림 50개 보내기(실패·재시도·DLQ·중복),  2 → 수신 거부와 방해 금지 시간"""
import random
import sys
from collections import Counter

from notify import Provider, Service


def clock(t):
    return f"{int(t // 3600) % 24:02d}:{int(t // 60) % 60:02d}"


def burst():
    rnd = random.Random(7)
    chans = ["push", "sms", "email"]
    provs = {"push": Provider(0.3, 1), "sms": Provider(0.3, 2, bad={"u3", "u9"}), "email": Provider(0.3, 28)}
    svc = Service(provs)
    reqs = [{"id": f"n{i}", "user": f"u{i % 20}", "to": f"u{i % 20}", "channel": chans[i % 3], "kind": "tx",
             "template": "ship", "data": {"order": 1000 + i}} for i in range(50)]
    reqs += rnd.sample(reqs, 10)                      # 앞 서비스가 응답을 못 받고 같은 요청을 다시 보냄
    rnd.shuffle(reqs)
    dup = sum(svc.submit(n) == "dup" for n in reqs)
    print(f"1) 요청 {len(reqs)}건 = 알림 50개 + 같은 id 다시 보낸 {len(reqs) - 50}건")
    print(f"   중복으로 버림 {dup}건")
    print("   채널     보냄  재시도  DLQ")
    tot = Counter()
    for ch in chans:
        r = svc.work(ch)
        sent = len(provs[ch].got)
        dlq = sum(m["channel"] == ch for m in svc.dlq)
        tot.update(sent=sent, retry=r, dlq=dlq)
        print(f"   {ch:<7} {sent:>4}  {r:>6}  {dlq:>3}")
    print(f"   합계    {tot['sent']:>4}  {tot['retry']:>6}  {tot['dlq']:>3}")
    got = [i for p in provs.values() for i in p.got]
    twice = sum(c > 1 for c in Counter(got).values())
    print(f"2) 제공자가 받은 알림 {len(got)}개 · 같은 id 두 번 {twice}개")
    for m in svc.dlq:
        print(f"   DLQ {m['id']} {m['channel']} {m['to']} · {m['why']}")


def prefs():
    provs = {ch: Provider(0.0, 1) for ch in ("push", "sms", "email")}
    svc = Service(provs, prefs={"u7": {"off": {"email"}, "quiet": (22, 8)}}, limit=2)
    svc.now = 23 * 3600                                   # 밤 11시
    print("1) u7 설정: 마케팅 메일 거부 · 방해 금지 22:00~08:00 · 마케팅 하루 2개")
    print(f"   지금 {clock(svc.now)}")
    rows = [("n1", "sms", "tx", "otp", {"code": 4821}), ("n2", "push", "mkt", "sale", {"title": "DDIA"}),
            ("n3", "email", "mkt", "sale", {"title": "DDIA"}), ("n4", "push", "mkt", "sale", {"title": "클린 코드"}),
            ("n5", "push", "mkt", "sale", {"title": "리팩터링"})]
    for i, ch, kind, tpl, data in rows:
        s = svc.submit({"id": i, "user": "u7", "to": "u7", "channel": ch, "kind": kind, "template": tpl, "data": data})
        print(f"   {i} {ch:<5} {'거래' if kind == 'tx' else '마케팅'}  → {s}")
    svc.work("sms"); first = clock(svc.now)
    svc.work("push")
    print(f"2) 인증번호는 {first}에 바로 보냄 · 마케팅 푸시는 {clock(svc.now)}까지 기다림")
    print(f"   보낸 것: {', '.join(provs['sms'].got + provs['push'].got)} · 메일은 0개")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "1"
    {"1": burst, "2": prefs}[arg]()
