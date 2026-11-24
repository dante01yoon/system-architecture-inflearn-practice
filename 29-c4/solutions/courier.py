"""연습 문제 풀이: 택배사(외부 시스템)를 붙이고, 검사를 통과시키고, 컨텍스트와 컨테이너 레벨에서 확인한다.
실행: python3 solutions/courier.py (c4 폴더에서)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bookshop import bookshop  # noqa: E402
from c4 import lint, outline  # noqa: E402

m = bookshop()
shop = m.diagrams[0].scope
orders = next(e for e in m.elements if e.name == "주문 서비스")
courier = m.system("택배사", "책을 배송한다", external=True)
shipping = m.container(shop, "배송 서비스", "배송을 맡기고 추적", "Python")
m.uses(orders, shipping, "배송을 요청한다", "JSON/HTTPS")
m.uses(shipping, courier, "집하를 요청한다", "HTTPS")
m.diagrams[0].show.append(courier)
m.diagrams[1].show += [shipping, courier]

print("문제", len(lint(m)), "개")
for d in m.diagrams[:2]:
    print(d.title)
    print("\n".join("   " + line for line in outline(m, d)))
