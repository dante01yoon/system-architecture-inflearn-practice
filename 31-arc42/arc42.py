"""arc42 열두 장 뼈대를 만들고, 채운 문서에서 빈 장과 9장의 ADR 링크를 검사한다."""
import re
from pathlib import Path

SECTIONS = ["소개와 목표", "제약", "컨텍스트와 범위", "해결 전략", "빌딩 블록 뷰", "런타임 뷰",
            "배포 뷰", "횡단 관심사", "아키텍처 결정", "품질 요구사항", "위험과 기술 부채", "용어집"]
MIN_CHARS = 40  # 이보다 짧으면 「짧음」(제목만 적고 미룬 장)


def skeleton(title):
    lines = [f"# {title} 아키텍처 문서 (arc42)", ""]
    for n, name in enumerate(SECTIONS, 1):
        lines += [f"## {n}. {name}", "<!-- 필요 없으면 「해당 없음」과 이유 한 줄 -->", ""]
    return "\n".join(lines)


def split(text):
    """## N. 제목 단위로 본문을 나눈다. {번호: 본문}"""
    parts = re.split(r"^## (\d+)\. .*$", text, flags=re.M)
    return {int(n): body for n, body in zip(parts[1::2], parts[2::2])}


def status(body):
    words = re.sub(r"<!--.*?-->", "", body, flags=re.S).strip()
    if not words:
        return "빈칸"
    if "TODO" in words or len(words) < MIN_CHARS:
        return "짧음"
    return "채움"


def check(path):
    doc = Path(path)
    body = split(doc.read_text(encoding="utf-8"))
    report = [(n, name, status(body.get(n, ""))) for n, name in enumerate(SECTIONS, 1)]
    linked = re.findall(r"\]\((adr/[^)]+\.md)\)", body.get(9, ""))
    files = sorted(f"adr/{p.name}" for p in (doc.parent / "adr").glob("*.md"))
    links = [(a, "연결됨" if a in files else "파일 없음") for a in linked]
    links += [(a, "9장에 없음") for a in files if a not in linked]
    return report, links
