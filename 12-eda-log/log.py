"""로그: 지우지 않고 뒤에 붙이기만 하는 파일. 소비자마다 어디까지 읽었는지(오프셋)를 따로 적는다."""
import json
from pathlib import Path


class Log:
    def __init__(self, path):
        self.path, self.offsets = Path(path), {}   # 소비자 이름 -> 다음에 읽을 줄 번호
        self.path.touch()

    def append(self, event):
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def read(self, consumer):
        lines = self.path.read_text(encoding="utf-8").splitlines()
        start = self.offsets.get(consumer, 0)
        return [(n, json.loads(line)) for n, line in enumerate(lines[start:], start)]

    def commit(self, consumer, offset):
        self.offsets[consumer] = offset + 1
