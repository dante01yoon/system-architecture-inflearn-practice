"""C4 모델을 파이썬 객체로 적고, 흔한 실수를 검사하고, 다이어그램마다 들여쓴 목록으로 보여 준다."""
from dataclasses import dataclass, field

KIND = {"person": "사람", "system": "시스템", "container": "컨테이너", "component": "컴포넌트"}
ALLOWED = {1: {"person", "system"}, 2: {"person", "system", "container"}, 3: {"person", "system", "container", "component"}}


@dataclass(eq=False)
class Element:
    kind: str
    name: str
    desc: str
    tech: str = ""
    parent: "Element | None" = None
    external: bool = False


@dataclass
class Rel:
    src: Element
    dst: Element
    desc: str
    tech: str = ""


@dataclass
class Diagram:
    title: str
    level: int
    scope: "Element | None"
    show: list = field(default_factory=list)


class Model:
    def __init__(self):
        self.elements, self.rels, self.diagrams = [], [], []

    def add(self, kind, name, desc, tech="", parent=None, external=False):
        e = Element(kind, name, desc, tech, parent, external)
        self.elements.append(e)
        return e

    def person(self, name, desc):
        return self.add("person", name, desc)

    def system(self, name, desc, external=False):
        return self.add("system", name, desc, external=external)

    def container(self, system, name, desc, tech=""):
        return self.add("container", name, desc, tech, system)

    def component(self, container, name, desc, tech=""):
        return self.add("component", name, desc, tech, container)

    def uses(self, src, dst, desc="", tech=""):
        self.rels.append(Rel(src, dst, desc, tech))

    def diagram(self, title, level, scope, show):
        self.diagrams.append(Diagram(title, level, scope, show))


def lint(model):
    """C4 표기 규칙 세 가지: 관계에는 설명, 컨테이너·컴포넌트에는 기술, 다이어그램 하나에는 한 레벨만."""
    problems = []
    for r in model.rels:
        if not r.desc:
            problems.append(f"설명 없는 관계: {r.src.name} → {r.dst.name}")
    for e in model.elements:
        if e.kind in ("container", "component") and not e.tech:
            problems.append(f"기술 없음: {e.name} [{KIND[e.kind]}]")
    for d in model.diagrams:
        for e in d.show:
            if e.kind not in ALLOWED[d.level] or (e.kind == "component" and e.parent is not d.scope):
                problems.append(f"레벨 섞임: {d.title}에 {KIND[e.kind]} 「{e.name}」")
    return problems


def _visible(e, shown):
    """e 자신이나 e를 품은 상위 요소 중 다이어그램에 보이는 것(지도를 축소하면 건물이 동네 점으로 합쳐지듯)."""
    while e is not None and e not in shown:
        e = e.parent
    return e


def lifted(model, d):  # 모든 관계를 이 다이어그램에 보이는 요소끼리의 관계로(같은 쌍은 한 번만)
    out = {}
    for r in model.rels:
        a, b = _visible(r.src, d.show), _visible(r.dst, d.show)
        if a and b and a is not b and (a, b) not in out:
            out[(a, b)] = Rel(a, b, r.desc, r.tech if d.level > 1 else "")
    return list(out.values())


def label(e):
    if e.external:
        return f"{e.name} [외부 시스템]"
    return f"{e.name} [{KIND[e.kind]}{' · ' + e.tech if e.tech else ''}]"


def short(e):
    return f"{e.name} [{'외부' if e.external else e.tech or KIND[e.kind]}]"


def outline(model, d):
    """다이어그램 하나를 들여쓴 목록으로: 보이는 요소마다 나가는 관계를 아래에(┃ = 확대한 범위 안), 나가는 관계가 없는 요소는 끝에 한 줄로."""
    rels = lifted(model, d)
    inside = [e for e in d.show if d.scope is not None and e.parent is d.scope]
    lines, leaves = [], []
    for e in d.show:
        mine = [r for r in rels if r.src is e]
        if not mine:
            leaves.append(e)
            continue
        pad = "┃ " if e in inside else ""
        lines.append(pad + label(e))
        lines += [f"{pad}  → {r.dst.name}: {r.desc}{f' ({r.tech})' if r.tech else ''}" for r in mine]
    if leaves:
        lines.append("그 밖: " + " · ".join(short(e) for e in leaves))
    return lines
