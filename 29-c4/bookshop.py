"""온라인 서점을 C4 모델로. messy=True면 흔한 실수 세 개가 섞인 판."""
from c4 import Model


def bookshop(messy=False):
    m = Model()
    customer = m.person("손님", "책을 고르고 주문한다")
    shop = m.system("온라인 서점", "책을 팔고 주문을 받는다")
    card = m.system("카드사", "카드 결제를 승인한다", external=True)
    mail = m.system("메일 발송", "주문 확인 메일을 보낸다", external=True)

    web = m.container(shop, "웹 앱", "손님이 보는 화면", "Python")
    catalog = m.container(shop, "카탈로그 서비스", "책 목록과 재고", "Python")
    orders = m.container(shop, "주문 서비스", "주문을 받고 처리", "Python")
    payment = m.container(shop, "결제 서비스", "카드사와 결제", "Python")
    db = m.container(shop, "서점 DB", "책·주문 저장", "" if messy else "PostgreSQL")

    api = m.component(orders, "주문 API", "주문 요청을 받는다", "Python")
    rules = m.component(orders, "주문 규칙", "재고와 금액을 확인한다", "Python")
    repo = m.component(orders, "주문 저장소", "주문을 DB에 쓴다", "Python · SQL")

    m.uses(customer, web, "책을 고르고 주문한다", "HTTPS")
    m.uses(web, catalog, "책 목록을 읽는다", "JSON/HTTPS")
    m.uses(web, api, "" if messy else "주문을 넣는다", "JSON/HTTPS")
    m.uses(catalog, db, "책을 읽는다", "SQL")
    m.uses(api, rules, "주문을 넘긴다")
    m.uses(rules, payment, "결제를 요청한다", "JSON/HTTPS")
    m.uses(rules, repo, "주문을 저장한다")
    m.uses(repo, db, "주문 행을 쓴다", "SQL")
    m.uses(rules, mail, "확인 메일을 부탁한다", "HTTPS")
    m.uses(payment, card, "결제 승인을 요청한다", "HTTPS")

    m.diagram("시스템 컨텍스트 다이어그램", 1, shop, [customer, shop, card, mail])
    m.diagram("컨테이너 다이어그램", 2, shop,
              [customer, web, catalog, orders, payment, db, card, mail] + ([repo] if messy else []))
    m.diagram("컴포넌트 다이어그램", 3, orders, [web, api, rules, repo, payment, db, mail])
    return m
