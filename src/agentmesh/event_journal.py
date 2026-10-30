"""R3 transactional SQLite event journal; opt-in, separate from legacy RunStore."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

class EventJournal:
    def __init__(self,path):
        self.path=str(Path(path).expanduser())
        Path(self.path).parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("""CREATE TABLE IF NOT EXISTS r3_runs(
                id TEXT PRIMARY KEY, created TEXT NOT NULL, status TEXT NOT NULL,
                accepted INTEGER NOT NULL, payload TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS r3_events(
                run_id TEXT NOT NULL, sequence INTEGER NOT NULL, agent TEXT NOT NULL,
                status TEXT NOT NULL, timestamp TEXT NOT NULL, payload TEXT NOT NULL,
                PRIMARY KEY(run_id,sequence),
                FOREIGN KEY(run_id) REFERENCES r3_runs(id))""")
            db.execute("CREATE INDEX IF NOT EXISTS idx_r3_runs ON r3_runs(created DESC)")
    def connect(self):
        db=sqlite3.connect(self.path,timeout=5)
        db.execute("PRAGMA foreign_keys=ON")
        return db
    def record(self,result):
        if not isinstance(result,dict) or not isinstance(result.get("trace"),list):
            raise ValueError("result must include trace")
        run_id=str(uuid4())
        now=datetime.now(timezone.utc).isoformat()
        trace=result["trace"]
        with self.connect() as db:
            db.execute("INSERT INTO r3_runs VALUES (?,?,?,?,?)",
                       (run_id,now,"completed",int(bool(result.get("accepted"))),
                        json.dumps(result,ensure_ascii=False,allow_nan=False)))
            for sequence,event in enumerate(trace,1):
                if not isinstance(event,dict):raise ValueError("invalid event")
                db.execute("INSERT INTO r3_events VALUES (?,?,?,?,?,?)",
                    (run_id,sequence,str(event.get("agent","unknown")),
                     str(event.get("status","unknown")),now,
                     json.dumps(event,ensure_ascii=False,allow_nan=False)))
        return run_id
    def list_runs(self,limit=30):
        if type(limit) is not int or not 1<=limit<=100:raise ValueError("limit out of range")
        with self.connect() as db:
            rows=db.execute("SELECT id,created,status,accepted FROM r3_runs ORDER BY created DESC LIMIT ?",(limit,)).fetchall()
        return [{"id":r[0],"created":r[1],"status":r[2],"accepted":bool(r[3])} for r in rows]
    def get_run(self,run_id):
        with self.connect() as db:
            row=db.execute("SELECT payload FROM r3_runs WHERE id=?",(run_id,)).fetchone()
        return json.loads(row[0]) if row else None
    def events(self,run_id,after=0,limit=100):
        if type(after) is not int or after<0 or type(limit) is not int or not 1<=limit<=500:
            raise ValueError("invalid cursor")
        with self.connect() as db:
            rows=db.execute("SELECT sequence,agent,status,timestamp,payload FROM r3_events WHERE run_id=? AND sequence>? ORDER BY sequence ASC LIMIT ?",(run_id,after,limit)).fetchall()
        return [{"sequence":n,"agent":a,"status":s,"timestamp":t,"payload":json.loads(p)}
                for n,a,s,t,p in rows]
