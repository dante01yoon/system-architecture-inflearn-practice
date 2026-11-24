"""온라인 서점 하나를 네 뷰로 적은 모델(파이썬 dict 하나). 뷰마다 「요소 → 이어진 요소들」."""
MODEL = {
    "logical": {        # 클래스 → 쓰는 클래스
        "Book": [],
        "Customer": [],
        "Cart": ["Book"],
        "Order": ["Customer", "Book"],
        "Payment": ["Order"],
        "Receipt": ["Order"],
    },
    "process": {        # 실행 중인 프로세스 → 메시지를 보내는 곳
        "web": ["order-worker"],
        "order-worker": ["payment-gw", "mailer"],
        "payment-gw": [],
        "mailer": [],
    },
    "development": {    # 모듈 → import 하는 모듈
        "shop/catalog": [],
        "shop/orders": ["shop/catalog"],
        "shop/payment": ["shop/orders"],
        "shop/mail": ["shop/orders"],
        "shop/web": ["shop/orders", "shop/catalog"],
    },
    "physical": {       # 서버 → 그 위에서 도는 프로세스
        "web-1": ["web"],
        "app-1": ["order-worker"],
        "pay-1": ["payment-gw"],
    },
}

ORDER_A_BOOK = [        # +1 시나리오: 단계마다 세 뷰의 요소를 짚는다
    {"step": "장바구니 담기", "logical": "Cart", "process": "web", "development": "shop/web"},
    {"step": "주문 만들기", "logical": "Order", "process": "order-worker", "development": "shop/orders"},
    {"step": "결제하기", "logical": "Payment", "process": "payment-gw", "development": "shop/payment"},
    {"step": "영수증 메일", "logical": "Receipt", "process": "mailer", "development": "shop/mail"},
]
