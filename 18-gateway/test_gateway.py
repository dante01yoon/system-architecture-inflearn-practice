import unittest

import gateway
import services
from client import App

ISBN = "9780134494166"


class GatewayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servers = [services.start(n) for n in services.PORTS] + [gateway.start()]

    @classmethod
    def tearDownClass(cls):
        for s in cls.servers:
            s.shutdown(), s.server_close()

    def test_book_page_is_one_trip_with_all_three_parts(self):
        app = App(gateway.TOKEN)
        status, page = app.get(8814, f"/book-page/{ISBN}")
        self.assertEqual((status, app.trips), (200, 1))
        self.assertEqual(page["catalog"]["title"], "Clean Architecture")
        self.assertEqual((page["reviews"]["count"], page["stock"]["left"]), (128, 3))

    def test_direct_calls_need_three_trips(self):
        app = App()
        for name, port in services.PORTS.items():
            app.get(port, f"/{name}/{ISBN}")
        self.assertEqual(app.trips, 3)

    def test_missing_token_is_rejected_at_the_gateway(self):
        status, body = App().get(8814, f"/catalog/{ISBN}")
        self.assertEqual(status, 401)

    def test_routes_by_path_prefix(self):
        status, body = App(gateway.TOKEN).get(8814, f"/stock/{ISBN}")
        self.assertEqual((status, body), (200, {"left": 3}))

    def test_dead_service_gives_partial_page(self):
        server = services.start("reviews", 8822)
        server.shutdown(), server.server_close()
        self.assertIsNone(gateway.fetch(8822, f"/reviews/{ISBN}"))


if __name__ == "__main__":
    unittest.main()
