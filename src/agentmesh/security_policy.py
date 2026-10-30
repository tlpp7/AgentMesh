"""R9 optional, explicit policy and bounded in-memory rate control.

Default-deny agent capabilities. No shell, network or implicit tool grants.
"""
from dataclasses import dataclass
from collections import deque
from threading import Lock
from time import monotonic

ROLE_PERMISSIONS={
 "viewer":frozenset(("runs:read",)),
 "operator":frozenset(("runs:read","runs:execute")),
 "supervisor":frozenset(("runs:read","runs:execute","tools:read")),
}
AGENT_CAPABILITIES={
 "analyzer":frozenset(("evaluate_trace",)),
 "proposer":frozenset(("review_issue",)),
 "critic":frozenset(("evaluate_trace","review_issue")),
}

@dataclass(frozen=True)
class Principal:
    identifier: str
    role: str
    def __post_init__(self):
        if not isinstance(self.identifier,str) or not self.identifier or len(self.identifier)>128:
            raise ValueError("invalid principal")
        if self.role not in ROLE_PERMISSIONS:raise ValueError("unknown role")

class Policy:
    def allowed(self,principal,permission):
        return isinstance(principal,Principal) and permission in ROLE_PERMISSIONS[principal.role]
    def agent_tool_allowed(self,agent,tool):
        return tool in AGENT_CAPABILITIES.get(agent,frozenset())

class SlidingWindowLimiter:
    def __init__(self,limit=30,window_seconds=60,clock=monotonic):
        if type(limit) is not int or not 1<=limit<=100000 or window_seconds<=0:
            raise ValueError("invalid limits")
        self.limit=limit
        self.window=float(window_seconds)
        self.clock=clock
        self.lock=Lock()
        self.hits={}
    def accept(self,key):
        if not isinstance(key,str) or not key:raise ValueError("invalid key")
        now=self.clock()
        with self.lock:
            q=self.hits.setdefault(key,deque())
            while q and q[0]<=now-self.window:q.popleft()
            if len(q)>=self.limit:return False
            q.append(now)
            return True
