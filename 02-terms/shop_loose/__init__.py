"""느슨한 서점: 주문은 「주문됨」 이벤트만 남기고, 나머지는 그 이벤트를 듣는다.
여기 __init__.py는 모듈을 불러와 구독을 등록하는 조립만 한다(coupling.py는 세지 않는다)."""
from shop_loose import email, events, orders, payment, stock  # noqa: F401
