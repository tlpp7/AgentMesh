"""Local SQLite run history with bounded event retrieval."""
import json
import sqlite3
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

class RunStore:
    def __init__(self,path):
        self.path=str(Path(path).expanduser())
        Path(self.path).parent.mkdir(parents=True,exist_ok=True)
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, created TEXT NOT NULL, mode TEXT NOT NULL, accepted INTEGER NOT NULL, payload TEXT NOT NULL)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_runs_created ON runs(created DESC)")
    def _connect(self):
        return sqlite3.connect(self.path,timeout=5)
    def append(self,mode,accepted,payload):
        if not isinstance(payload,dict): raise ValueError("payload must be dict")
        identifier=str(uuid4())
        now=datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            db.execute("INSERT INTO runs VALUES (?,?,?,?,?)",
                       (identifier,now,str(mode),int(bool(accepted)),json.dumps(payload,allow_nan=False)))
        return identifier
    def list(self,limit=30):
        if not 1<=limit<=100: raise ValueError("limit outside 1..100")
        with self._connect() as db:
            rows=db.execute("SELECT id,created,mode,accepted FROM runs ORDER BY created DESC LIMIT ?",(limit,)).fetchall()
        return [{"id":i,"created":c,"mode":m,"accepted":bool(a)} for i,c,m,a in rows]
    def prune(self, keep=1000):
        """Keep newest N runs. Must be explicitly invoked."""
        if type(keep) is not int or not 1<=keep<=100000:
            raise ValueError("keep must be 1..100000")
        with self._connect() as db:
            cursor=db.execute("DELETE FROM runs WHERE id IN (SELECT id FROM runs ORDER BY created DESC, rowid DESC LIMIT -1 OFFSET ?)",(keep,))
            return cursor.rowcount

    def backup(self, destination):
        """Consistent SQLite backup; refuse overwriting source."""
        target=Path(destination).expanduser().resolve()
        if target==Path(self.path).resolve():
            raise ValueError("backup destination must differ from source")
        target.parent.mkdir(parents=True,exist_ok=True)
        with self._connect() as source:
            with sqlite3.connect(str(target),timeout=5) as other:
                source.backup(other)
        return str(target)

    def get(self,identifier):
        with self._connect() as db:
            row=db.execute("SELECT payload FROM runs WHERE id=?",(identifier,)).fetchone()
        return json.loads(row[0]) if row else None
