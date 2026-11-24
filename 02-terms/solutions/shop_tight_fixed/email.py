outbox = []


def send(to, text):
    outbox.append((to, text))


def send_admin(text):
    send("admin", text)
