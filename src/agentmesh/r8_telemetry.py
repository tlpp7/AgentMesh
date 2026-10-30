"""R8 bounded, thread-safe in-process execution telemetry.

No content, tokens, or agent outputs are recorded. Not distributed tracing.
"""
from collections import deque
from datetime import datetime, timezone
from threading import Lock
from time import perf_counter
from uuid import uuid4
from math import isfinite

class RunTelemetry:
    def __init__(self,capacity=200):
        if type(capacity) is not int or not 1<=capacity<=10000:
            raise ValueError("invalid telemetry capacity")
        self._events=deque(maxlen=capacity)
        self._lock=Lock()

    def record(self,*,accepted,duration_ms,run_id=None,event_count=0):
        if not isinstance(duration_ms,(float,int)) or not isfinite(duration_ms) or duration_ms<0:
            raise ValueError("invalid duration")
        if type(event_count) is not int or event_count<0:
            raise ValueError("invalid event count")
        entry={"trace_id":uuid4().hex,"run_id":run_id,"accepted":bool(accepted),
               "duration_ms":round(duration_ms,3),"event_count":event_count,
               "timestamp":datetime.now(timezone.utc).isoformat()}
        with self._lock:self._events.append(entry)
        return dict(entry)

    def snapshot(self,limit=30):
        if type(limit) is not int or not 1<=limit<=100:
            raise ValueError("invalid limit")
        with self._lock:entries=list(self._events)[-limit:][::-1]
        durations=sorted(e["duration_ms"] for e in entries)
        n=len(entries)
        p95=durations[min(n-1,int((n-1)*.95))] if n else None
        return {"schema_version":1,"scope":"single_process_memory","count":n,
                "accepted_count":sum(e["accepted"] for e in entries),
                "p95_duration_ms":p95,"runs":entries}
