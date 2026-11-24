"""문(facade): 모든 요청을 받아 길 안내표대로 레거시나 새 서비스로 보낸다."""
import legacy
import newshop

SYSTEMS = {"legacy": legacy, "new": newshop}


class Facade:
    def __init__(self, routes):
        self.routes = dict(routes)   # 기능 이름 → "legacy" · "new" · "compare"
        self.compared = []           # 나란히 돌린 결과: (기능, isbn, 같았나)

    def handle(self, name, isbn, *args):
        where = self.routes[name]
        if where == "compare":       # 나란히 돌리기
            old = getattr(legacy, name)(isbn, *args)
            new = getattr(newshop, name)(isbn, *args)
            self.compared.append((name, isbn, old == new))
            return "legacy", old
        return where, getattr(SYSTEMS[where], name)(isbn, *args)
