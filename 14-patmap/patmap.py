"""증상 한 줄을 받아, 패턴 지도에서 가장 많이 맞는 패턴과 그 대가를 알려 준다."""
import sys

# (패턴, 증상 낱말, 문제, 대가, 배울 수업)
MAP = [
    ("CQRS", ["조회", "읽기", "화면", "모양"],
     "읽기와 쓰기가 원하는 모양이 다르다", "결과적 일관성 · 저장소 둘", "CQRS"),
    ("Saga", ["트랜잭션", "여러 서비스", "되돌", "결제"],
     "여러 서비스에 걸친 트랜잭션", "되돌리는 일을 직접 짠다", "Saga ① ②"),
    ("API Gateway", ["클라이언트", "입구", "주소", "인증"],
     "클라이언트도 많고 서비스도 많다", "문 하나가 병목이 될 수 있다", "API Gateway"),
    ("Circuit Breaker", ["느려", "멈춰", "장애", "번져"],
     "의존하는 곳 하나가 모두를 끌어내린다", "실패 때 보여 줄 답을 따로 준비", "Circuit Breaker · Bulkhead"),
    ("Event Sourcing", ["이력", "기록", "언제", "감사"],
     "바뀐 과정을 전부 남겨야 한다", "지금 상태는 다시 계산해야 한다", "이벤트 소싱"),
    ("Strangler Fig", ["레거시", "옛 시스템", "교체", "갈아"],
     "옛 시스템을 조금씩 바꿔야 한다", "한동안 둘을 같이 돌린다", "Strangler Fig"),
    ("Hexagonal", ["프레임워크", "테스트", "엉켜", "섞여"],
     "업무 규칙이 프레임워크와 엉켜 있다", "인터페이스와 어댑터가 늘어난다", "의존성 규칙 · 헥사고날"),
    ("Queue-Based Load Leveling", ["몰려", "폭주", "한꺼번에", "세일"],
     "요청이 한순간에 몰린다", "처리가 늦어진다 · 큐 길이를 지켜본다", "큐로 폭주 받아 내기"),
]


def find(symptom):
    """가장 많은 낱말이 맞는 칸과 맞은 낱말들. 하나도 안 맞으면 None."""
    best, hits = None, []
    for row in MAP:
        got = [w for w in row[1] if w in symptom]
        if len(got) > len(hits):  # 같으면 지도에서 먼저 나온 칸
            best, hits = row, got
    return (best, hits) if best else None


def answer(symptom):
    found = find(symptom)
    if not found:
        return ["   맞는 칸이 없어요. 증상을 더 구체적으로 적어 보세요"]
    (name, _, problem, cost, lesson), hits = found
    return [f"   맞은 낱말: {', '.join(hits)}", f"   문제 -> {problem}",
            f"   패턴 -> {name}", f"   대가 -> {cost}", f"   수업 -> {lesson}"]


if __name__ == "__main__":
    print("\n".join(answer(" ".join(sys.argv[1:]))))
