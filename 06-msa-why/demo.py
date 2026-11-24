"""카탈로그만 새 버전으로 배포하는 동안 주문 서비스가 계속 답하는지, 모놀리스와 나란히 본다."""
import time

from catalog import catalog_server
from monolith import monolith_server
from order import order_server
from serve import get, start, stop

CATALOG, ORDER, MONO = 8701, 8702, 8703
ASK = "/order?book=Clean%20Architecture&qty=2"
T0 = time.monotonic()


def log(text):
    print(f"   [{time.monotonic() - T0:4.1f}초] {text}")


def ask(name, port):
    r = get(f"http://127.0.0.1:{port}{ASK}")
    log(f"{name} 주문 2권 -> " + (f"합계 {r['total']}원 ({r['note']})" if "total" in r else f"실패: {r['error']}"))
    return r


def main():
    print("1) 서비스 둘을 띄운다: catalog v1, order")
    catalog = start(catalog_server(CATALOG, 1))
    order = start(order_server(ORDER, f"http://127.0.0.1:{CATALOG}"))
    ask("order", ORDER)

    print("2) catalog만 v2로 배포 (내렸다 다시 띄움)")
    stop(catalog)
    log("catalog 내림")
    ask("order", ORDER)
    time.sleep(1)
    catalog = start(catalog_server(CATALOG, 2))
    log("catalog v2 올림")
    r = ask("order", ORDER)
    print(f"   order는 한 번도 안 내림: 켠 뒤 받은 주문 {r['orders']}건")

    print("3) 비교: 모놀리스는 값 규칙 하나에도 전체를 다시 띄운다")
    mono = start(monolith_server(MONO, 1))
    ask("monolith", MONO)
    stop(mono)
    log("monolith 내림")
    ask("monolith", MONO)
    time.sleep(1)
    mono = start(monolith_server(MONO, 2))
    log("monolith v2 올림")
    ask("monolith", MONO)

    stop(order), stop(catalog), stop(mono)


if __name__ == "__main__":
    main()
