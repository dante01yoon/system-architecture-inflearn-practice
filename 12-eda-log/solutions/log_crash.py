"""연습 문제 풀이: 로그 소비자가 재고를 뺀 뒤 오프셋을 저장하기 전에 죽으면, 다시 켜졌을 때 같은 줄을 또 읽는다(최소 한 번).
take_once(처리한 번호 표)를 쓰면 다시 읽어도 재고가 맞다."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from consumer import left, open_db, take, take_once  # noqa: E402
from log import Log  # noqa: E402

for handle in (take, take_once):
    log, db = Log(Path(tempfile.mkdtemp()) / "orders.log"), open_db()
    for i in (1, 2, 3):
        log.append({"id": f"m{i}", "book": "DDIA", "qty": 1})
    for n, e in log.read("stock"):
        handle(db, e)
        if n == 1:
            break  # m2를 처리하고 commit 전에 죽음 -> 오프셋은 1에 머문다
        log.commit("stock", n)
    for n, e in log.read("stock"):  # 다시 켜짐: 오프셋 1(m2)부터
        handle(db, e)
        log.commit("stock", n)
    print(f"{handle.__name__}: 재고 {left(db)}권 (기대 7권)")
