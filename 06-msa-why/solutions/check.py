"""연습 문제 확인: catalog가 내려간 동안 처음 보는 책을 주문하면?"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from catalog import catalog_server  # noqa: E402
from order import order_server  # noqa: E402
from serve import get, start, stop  # noqa: E402

catalog = start(catalog_server(0, 1))
cport = catalog.server_address[1]
order = start(order_server(0, f"http://127.0.0.1:{cport}"))
base = f"http://127.0.0.1:{order.server_address[1]}/order?qty=1&book="
print("Clean Architecture:", get(base + "Clean%20Architecture"))
stop(catalog)
print("catalog 내린 뒤 Release It!:", get(base + "Release%20It!"))
stop(order)
