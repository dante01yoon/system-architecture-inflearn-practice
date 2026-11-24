import unittest

from bookshop import bookshop
from c4 import Model, lifted, lint, outline


class C4Test(unittest.TestCase):
    def test_messy_model_has_exactly_three_mistakes(self):
        problems = lint(bookshop(messy=True))
        self.assertEqual(len(problems), 3)
        self.assertTrue(problems[0].startswith("설명 없는 관계: 웹 앱 → 주문 API"))
        self.assertTrue(problems[1].startswith("기술 없음: 서점 DB"))
        self.assertTrue(problems[2].startswith("레벨 섞임: 컨테이너 다이어그램에 컴포넌트"))

    def test_fixed_model_is_clean(self):
        self.assertEqual(lint(bookshop()), [])

    def test_component_relations_are_lifted_when_zooming_out(self):
        m = bookshop()
        context, containers, _ = m.diagrams
        pairs = {(r.src.name, r.dst.name) for r in lifted(m, context)}
        self.assertEqual(pairs, {("손님", "온라인 서점"), ("온라인 서점", "메일 발송"), ("온라인 서점", "카드사")})
        self.assertTrue(all(r.tech == "" for r in lifted(m, context)))  # 컨텍스트에서는 기술을 숨긴다
        pairs2 = {(r.src.name, r.dst.name) for r in lifted(m, containers)}
        self.assertIn(("주문 서비스", "서점 DB"), pairs2)  # 주문 저장소 → 서점 DB가 컨테이너 수준으로 올라옴

    def test_component_from_another_container_mixes_levels(self):
        m = Model()
        s = m.system("S", "s")
        a, b = m.container(s, "A", "a", "Py"), m.container(s, "B", "b", "Py")
        x = m.component(b, "X", "x", "Py")
        m.diagram("컴포넌트 다이어그램", 3, a, [x])
        self.assertEqual(lint(m), ["레벨 섞임: 컴포넌트 다이어그램에 컴포넌트 「X」"])

    def test_outline_marks_zoomed_scope(self):
        m = bookshop()
        lines = outline(m, m.diagrams[2])
        self.assertIn("┃ 주문 API [컴포넌트 · Python]", lines)
        self.assertTrue(lines[-1].startswith("그 밖:"))


if __name__ == "__main__":
    unittest.main()
