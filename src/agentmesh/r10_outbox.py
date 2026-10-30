"""R10: additive durable transactional outbox backed by SQLite.

Separate from the R3 journal, with idempotent event insertion and explicit acknowledgement.
"""
import json
import sqlite3
from datetime import datetime,timezone
from pathlib import Path
from uuid import uuid4

class DurableOutbox:
    def __init__(self,path):
        self.path=str(Path(path).expanduser())
        Path(self.path).parent.mkdir(parents=True,exist_ok=True)
        with self._db() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("""CREATE TABLE IF NOT EXISTS r10_outbox(
              event_id TEXT PRIMARY KEY, stream TEXT NOT NULL, kind TEXT NOT NULL,
              payload TEXT NOT NULL, created TEXT NOT NULL,
              delivered TEXT, attempts INTEGER NOT NULL DEFAULT 0)""")
            db.execute("CREATE INDEX IF NOT EXISTS idx_r10_pending ON r10_outbox(delivered,created,event_id)")
    def _db(self):
        return sqlite3.connect(self.path,timeout=5)
    def put(self,stream,kind,payload,event_id=None):
        if not all(isinstance(v,str) and 1<=len(v)<=128 for v in (stream,kind)):
            raise ValueError("invalid stream or kind")
        if not isinstance(payload,dict):raise ValueError("payload must be object")
        identifier=event_id if event_id is not None else str(uuid4())
        try:
            identifier=str(uuid4()) if event_id is None else str(__import__("uuid").UUID(event_id))
        except (ValueError,TypeError,AttributeError) as exc:
            raise ValueError("event_id must be UUID") from exc
        data=json.dumps(payload,ensure_ascii=False,allow_nan=False,sort_keys=True)
        now=datetime.now(timezone.utc).isoformat()
        with self._db() as db:
            db.execute("INSERT OR IGNORE INTO r10_outbox(event_id,stream,kind,payload,created) VALUES (?,?,?,?,?)",
                       (identifier,stream,kind,data,now))
            row=db.execute("SELECT stream,kind,payload FROM r10_outbox WHERE event_id=?",(identifier,)).fetchone()
            if row!=(stream,kind,data):
                raise ValueError("idempotency key reused with different event")
        return identifier
    def pending(self,limit=50):
        if type(limit) is not int or not 1<=limit<=500:raise ValueError("invalid limit")
        with self._db() as db:
            rows=db.execute("SELECT event_id,stream,kind,payload,created,attempts FROM r10_outbox WHERE delivered IS NULL ORDER BY created,event_id LIMIT ?",(limit,)).fetchall()
        return [{"event_id":i,"stream":s,"kind":k,"payload":json.loads(p),"created":c,"attempts":a}
                for i,s,k,p,c,a in rows]
    def acknowledge(self,event_id):
        with self._db() as db:
            cursor=db.execute("UPDATE r10_outbox SET delivered=? WHERE event_id=? AND delivered IS NULL",
                              (datetime.now(timezone.utc).isoformat(),event_id))
        return cursor.rowcount==1
    def mark_attempt(self,event_id):
        with self._db() as db:
            cursor=db.execute("UPDATE r10_outbox SET attempts=attempts+1 WHERE event_id=? AND delivered IS NULL",(event_id,))
        return cursor.rowcount==1
