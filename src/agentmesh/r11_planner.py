"""R11 bounded priority-aware DAG scheduler (additive to AsyncMesh)."""
import asyncio
from dataclasses import dataclass
from time import monotonic
from typing import Awaitable,Callable

@dataclass(frozen=True)
class PlanNode:
    name:str
    execute:Callable[[dict[str,str],str],Awaitable[str]]
    depends_on:tuple[str,...]=()
    priority:int=0
    def __post_init__(self):
        if not self.name or not self.name.isidentifier():raise ValueError("invalid name")
        if type(self.priority) is not int or not -100<=self.priority<=100:raise ValueError("invalid priority")

class DynamicPlanner:
    def __init__(self,nodes,concurrency=4,max_nodes=64,timeout_seconds=30):
        nodes=list(nodes)
        if type(concurrency) is not int or not 1<=concurrency<=32:raise ValueError("invalid concurrency")
        if type(max_nodes) is not int or not 1<=max_nodes<=256:raise ValueError("invalid max_nodes")
        if not 0<timeout_seconds<=3600 or not nodes or len(nodes)>max_nodes:raise ValueError("invalid node count or timeout")
        if len({n.name for n in nodes})!=len(nodes):raise ValueError("duplicate nodes")
        self.nodes={n.name:n for n in nodes}
        self.concurrency=concurrency
        self.timeout_seconds=timeout_seconds
        self._validate()
    def _validate(self):
        visited=set()
        visiting=set()
        def visit(name):
            if name in visiting:raise ValueError("dependency cycle")
            if name in visited:return
            visiting.add(name)
            for dep in self.nodes[name].depends_on:
                if dep not in self.nodes:raise ValueError("unknown dependency")
                visit(dep)
            visiting.remove(name)
            visited.add(name)
        for name in self.nodes:visit(name)
    async def run(self,objective,cancel_event=None):
        if not isinstance(objective,str) or not objective.strip():raise ValueError("invalid objective")
        pending=set(self.nodes)
        running={}
        outputs={}
        errors={}
        trace=[]
        started=monotonic()
        async def execute(node):
            args={dep:outputs[dep] for dep in node.depends_on}
            return await asyncio.wait_for(node.execute(args,objective),self.timeout_seconds)
        while pending or running:
            cancelled=cancel_event is not None and cancel_event.is_set()
            if cancelled:
                for task in running:task.cancel()
                for task in list(running):
                    try:await task
                    except BaseException:pass
                    errors[running[task]]="cancelled"
                running.clear()
                for name in pending:errors[name]="cancelled"
                pending.clear()
                break
            blocked=[name for name in pending if any(dep in errors for dep in self.nodes[name].depends_on)]
            for name in sorted(blocked):
                pending.remove(name)
                errors[name]="dependency_failed"
                trace.append({"agent":name,"status":"blocked"})
            ready=sorted((name for name in pending if all(dep in outputs for dep in self.nodes[name].depends_on)),
                         key=lambda name:(-self.nodes[name].priority,name))
            for name in ready[:max(0,self.concurrency-len(running))]:
                pending.remove(name)
                task=asyncio.create_task(execute(self.nodes[name]))
                running[task]=name
                trace.append({"agent":name,"status":"started"})
            if not running:continue
            done,_=await asyncio.wait(running,timeout=.05,return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                name=running.pop(task)
                try:
                    value=task.result()
                    if not isinstance(value,str):raise TypeError("node output must be string")
                    outputs[name]=value
                    trace.append({"agent":name,"status":"completed"})
                except BaseException as exc:
                    errors[name]=type(exc).__name__
                    trace.append({"agent":name,"status":"failed","error_type":type(exc).__name__})
        return {"accepted":not errors,"outputs":outputs,"errors":errors,
                "trace":trace,"duration_ms":round((monotonic()-started)*1000,3)}
