"""코어: 주문의 뼈대만. 금액을 바꾸는 규칙은 플러그인이 붙인다."""
import importlib
import pkgutil

from microkernel import plugins

BOOKS = {"Clean Architecture": 32000, "Release It!": 28000}
RULES = []


def register(rule):
    RULES.append(rule)
    return rule


def load_plugins():
    for m in pkgutil.iter_modules(plugins.__path__):
        importlib.import_module(f"{plugins.__name__}.{m.name}")


def place_order(req):
    amount = BOOKS[req["title"]] * req["qty"]
    for rule in RULES:
        amount = rule(req, amount)
    return amount
