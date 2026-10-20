import json
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path


class Store:
    def __init__(self, filename, clock=time.time):
        self.filename, self.clock = str(filename), clock
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            db.execute("pragma journal_mode=wal")
            db.execute(
                "create table if not exists objects (kind text, identity text, video text, provider text, body text, expiry real, touched real, primary key(kind,identity))"
            )
            db.execute("create index if not exists recent on objects(kind,video,provider,touched)")

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.filename, timeout=8)
        try:
            with db:
                yield db
        finally:
            db.close()

    def read(self, kind, identity):
        with self.connection() as db:
            db.execute("delete from objects where expiry<=?", (self.clock(),))
            row = db.execute(
                "select body,expiry from objects where kind=? and identity=?", (kind, identity)
            ).fetchone()
        return (json.loads(row[0]), row[1]) if row else None

    def write(self, kind, identity, video, provider, body, lifetime):
        encoded = json.dumps(body, ensure_ascii=False)
        if len(encoded.encode()) > 1500000:
            return None
        now = self.clock()
        with self.connection() as db:
            db.execute("delete from objects where expiry<=?", (now,))
            db.execute(
                "insert or replace into objects values(?,?,?,?,?,?,?)",
                (kind, identity, video, provider, encoded, now + lifetime, now),
            )
            db.execute(
                "delete from objects where rowid in (select rowid from objects where kind=? order by touched desc limit -1 offset ?)",
                (kind, 100 if kind == "source" else 500),
            )
        return now + lifetime

    def latest(self, video, provider):
        with self.connection() as db:
            row = db.execute(
                "select body,expiry from objects where kind='review' and video=? and provider=? and expiry>? order by touched desc limit 1",
                (video, provider, self.clock()),
            ).fetchone()
        return (json.loads(row[0]), row[1]) if row else None
