"""트랜잭션과 격리: 갱신 손실(SQLite, 연결 두 개 + 스레드)과 write skew(스냅샷 격리 장난감 모델)."""
import sqlite3
import threading


def open_db(path, stock):
    db = sqlite3.connect(path, isolation_level=None)
    db.executescript("DROP TABLE IF EXISTS books; CREATE TABLE books(id INTEGER PRIMARY KEY, title TEXT, stock INTEGER);")
    db.execute("INSERT INTO books VALUES (1, '데이터 중심 애플리케이션 설계', ?)", (stock,))
    db.close()


def clerks(path, work):
    """점원 A·B가 각자 연결로 work(연결, 이름, 차례)를 돌린다. 차례는 A읽기 → B읽기 → A쓰기 → B쓰기로 고정."""
    turn = [threading.Event() for _ in range(5)]
    log = []

    def run(name, mine):
        db = sqlite3.connect(path, isolation_level=None, timeout=5)
        work(db, name, lambda k: turn[mine[k]].wait(), lambda k: turn[mine[k] + 1].set(), log)
        db.close()

    a = threading.Thread(target=run, args=("점원A", (0, 2)))
    b = threading.Thread(target=run, args=("점원B", (1, 3)))
    a.start(); b.start(); turn[0].set(); a.join(); b.join()
    return log


def sell_read_then_write(db, name, wait, done, log):
    """흔한 코드 모양: 읽기와 쓰기를 따로 보낸다(그 사이에 끼어들 수 있다)."""
    wait(0)
    stock = db.execute("SELECT stock FROM books WHERE id = 1").fetchone()[0]
    log.append(f"{name} 읽기: 재고 {stock}")
    done(0); wait(1)
    db.execute("BEGIN IMMEDIATE")
    db.execute("UPDATE books SET stock = ? WHERE id = 1", (stock - 1,))
    db.execute("COMMIT")
    log.append(f"{name} 쓰기: 재고 = {stock - 1}")
    done(1)


def sell_atomic(db, name, wait, done, log):
    """고침: 읽고-계산하고-쓰기를 데이터베이스 안의 한 문장으로."""
    wait(0); done(0); wait(1)
    n = db.execute("UPDATE books SET stock = stock - 1 WHERE id = 1 AND stock > 0").rowcount
    log.append(f"{name}: {'팔림' if n else '품절'} (바뀐 줄 {n})")
    done(1)


def stock(path):
    db = sqlite3.connect(path)
    s = db.execute("SELECT stock FROM books WHERE id = 1").fetchone()[0]
    db.close()
    return s


# ── 장난감 MVCC: 실제 데이터베이스가 아니라, 스냅샷 격리의 규칙만 흉내 낸 모델 ──
class Conflict(Exception):
    pass


class Store:
    """값마다 버전 목록 [(커밋 번호, 값)]. 스냅샷 = 시작할 때의 커밋 번호."""
    def __init__(self, data):
        self.clock = 0
        self.versions = {k: [(0, v)] for k, v in data.items()}

    def begin(self):
        return Txn(self, self.clock)


class Txn:
    def __init__(self, store, snap):
        self.store, self.snap, self.writes = store, snap, {}

    def read(self, key):
        if key in self.writes:
            return self.writes[key]
        mine = [v for ts, v in self.store.versions.get(key, []) if ts <= self.snap]
        return mine[-1] if mine else None   # 스냅샷 뒤에 생긴 값은 안 보임

    def write(self, key, value):
        self.writes[key] = value

    def commit(self):
        """먼저 커밋한 쪽이 이긴다. 내가 쓴 값만 검사한다(읽기만 한 값은 안 본다)."""
        for k in self.writes:
            last = self.store.versions.get(k, [(0, None)])[-1][0]
            if last > self.snap:
                raise Conflict(k)
        self.store.clock += 1
        for k, v in self.writes.items():
            self.store.versions.setdefault(k, []).append((self.store.clock, v))


CASHIERS = ["민지", "준호"]


def on_duty(tx):
    return sum(tx.read(f"근무:{c}") for c in CASHIERS)


def leave(tx, me, lock_row=False):
    """퇴근 규칙: 계산대에 한 명은 남아야 한다. 두 명 이상이면 빠져도 된다."""
    n = on_duty(tx)
    if n >= 2:
        tx.write(f"근무:{me}", 0)
        if lock_row:
            tx.write("교대표", tx.read("교대표") + 1)   # 충돌을 한 줄로
    return n


def cashier_store():
    return Store({"근무:민지": 1, "근무:준호": 1, "교대표": 0})
