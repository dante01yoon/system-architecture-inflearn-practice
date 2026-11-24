"""서비스 의존 설명을 읽어 아키텍처 퀀텀(함께 묶여 움직이는 서비스 무리)을 찾는다."""


def parse(text):
    services, links = [], []
    for raw in text.splitlines():
        words = raw.split("#")[0].split()
        if not words:
            continue
        kind, *names = words
        if kind not in ("sync", "async", "db"):
            raise ValueError(f"모르는 줄: {raw}")
        users = names[1:] if kind == "db" else names
        services += [n for n in users if n not in services]
        links.append((kind, users))
    return services, links


def quanta(services, links):
    leader = {s: s for s in services}

    def find(s):
        while leader[s] != s:
            s = leader[s]
        return s

    for kind, users in links:
        if kind == "async":
            continue  # 메시지는 기다리지 않는다: 묶지 않는다
        for other in users[1:]:
            leader[find(other)] = find(users[0])

    groups = {}
    for s in services:
        groups.setdefault(find(s), []).append(s)
    return list(groups.values())
