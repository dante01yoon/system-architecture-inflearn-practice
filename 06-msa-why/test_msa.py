import unittest

from catalog import catalog_server
from monolith import monolith_server
from order import order_server
from serve import get, start, stop

ASK = "/order?book=Release%20It!&qty=3"


def port(server):
    return server.server_address[1]


class MsaTest(unittest.TestCase):
    def test_order_survives_catalog_redeploy(self):
        catalog = start(catalog_server(0, 1))
        cport = port(catalog)
        order = start(order_server(0, f"http://127.0.0.1:{cport}"))
        url = f"http://127.0.0.1:{port(order)}{ASK}"
        self.assertEqual(get(url)["total"], 90000)
        stop(catalog)
        down = get(url)
        self.assertEqual((down["total"], down["note"]), (90000, "저장해 둔 값"))
        catalog = start(catalog_server(cport, 2))
        up = get(url)
        self.assertEqual((up["total"], up["note"], up["orders"]), (81000, "catalog v2", 3))
        stop(order), stop(catalog)

    def test_order_without_any_price_reports_error(self):
        order = start(order_server(0, "http://127.0.0.1:9"))
        self.assertEqual(get(f"http://127.0.0.1:{port(order)}{ASK}"), {"error": "카탈로그 응답 없음"})
        stop(order)

    def test_monolith_is_down_while_redeploying(self):
        mono = start(monolith_server(0, 1))
        url = f"http://127.0.0.1:{port(mono)}{ASK}"
        self.assertEqual(get(url)["total"], 90000)
        stop(mono)
        self.assertEqual(get(url), {"error": "연결 안 됨"})


if __name__ == "__main__":
    unittest.main()
