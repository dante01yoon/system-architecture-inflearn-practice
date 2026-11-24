import unittest

from patmap import answer, find

CASES = {
    "주문 내역 화면 조회가 무겁고, 쓰는 표와 모양이 달라요": "CQRS",
    "주문과 결제가 여러 서비스에 걸친 트랜잭션이에요": "Saga",
    "앱 클라이언트마다 서비스 주소를 다 알아야 해요": "API Gateway",
    "추천 서비스가 느려지면 주문까지 멈춰요": "Circuit Breaker",
    "가격이 언제 바뀌었는지 이력을 다 남겨야 해요": "Event Sourcing",
    "옛 시스템을 한 번에 교체하기 무서워요": "Strangler Fig",
    "업무 규칙이 프레임워크와 엉켜서 테스트가 어려워요": "Hexagonal",
    "연말 세일에 주문이 한꺼번에 몰려요": "Queue-Based Load Leveling",
}


class PatmapTest(unittest.TestCase):
    def test_each_symptom_finds_its_pattern(self):
        for symptom, name in CASES.items():
            self.assertEqual(find(symptom)[0][0], name, symptom)

    def test_unknown_symptom_says_so(self):
        self.assertIsNone(find("배송 상자 색을 바꾸고 싶어요"))
        self.assertIn("맞는 칸이 없어요", answer("배송 상자 색을 바꾸고 싶어요")[0])


if __name__ == "__main__":
    unittest.main()
