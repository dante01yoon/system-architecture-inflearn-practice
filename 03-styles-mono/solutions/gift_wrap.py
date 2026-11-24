"""연습 문제 풀이(마이크로커널): 선물 포장 플러그인. microkernel/plugins/에 복사하면 코어를 고치지 않고 붙는다."""
from microkernel.core import register


@register
def gift_wrap(req, amount):
    return amount + 2000 if req.get("gift") else amount
