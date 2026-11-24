"""덧붙이기만 하는 이벤트 저장소(sqlite3). 책 한 권마다 이벤트 줄(stream) 하나."""
import json
import sqlite3


class Conflict(Exception):
    """내가 읽은 뒤에 누가 먼저 이벤트를 붙였다."""


class EventStore:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS events (stream, version, type, schema,"
                        " data, day, PRIMARY KEY (stream, version))")
        self.db.execute("CREATE TABLE IF NOT EXISTS snapshots (stream, version, state,"
                        " PRIMARY KEY (stream, version))")

    def append(self, stream, expected, type, data, day, schema=2):
        row = (stream, expected + 1, type, schema, json.dumps(data, ensure_ascii=False), day)
        try:
            with self.db:
                self.db.execute("INSERT INTO events VALUES (?, ?, ?, ?, ?, ?)", row)
        except sqlite3.IntegrityError:
            raise Conflict(f"{stream} v{expected + 1}은 이미 있음")
        return expected + 1

    def read(self, stream, after=0, until_day="9999"):
        rows = self.db.execute("SELECT version, type, schema, data, day FROM events"
                               " WHERE stream = ? AND version > ? AND day <= ?"
                               " ORDER BY version", (stream, after, until_day))
        return [(v, t, s, json.loads(d), day) for v, t, s, d, day in rows]

    def save_snapshot(self, stream, version, state):
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO snapshots VALUES (?, ?, ?)",
                            (stream, version, json.dumps(state)))

    def last_snapshot(self, stream):
        row = self.db.execute("SELECT version, state FROM snapshots WHERE stream = ?"
                              " ORDER BY version DESC LIMIT 1", (stream,)).fetchone()
        return (row[0], json.loads(row[1])) if row else (0, None)
