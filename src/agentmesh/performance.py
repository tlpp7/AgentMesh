"""P4 synthetic performance benchmarks; no remote API calls."""
import asyncio
import math
import statistics
import tracemalloc
from dataclasses import dataclass,asdict
from time import perf_counter
from .async_engine import AsyncAgent,AsyncMesh

def percentile(values,percent):
    if not values or not 0<=percent<=100:raise ValueError("invalid percentile")
    seq=sorted(values)
    idx=(len(seq)-1)*percent/100
    left=math.floor(idx)
    return seq[left]+(seq[math.ceil(idx)]-seq[left])*(idx-left)

@dataclass(frozen=True)
class BenchmarkConfig:
    agents:int=20
    concurrency:int=4
    delay_ms:float=2.0
    runs:int=8
    failure_every:int=0
    graph:str="independent"
    def __post_init__(self):
        if not 1<=self.agents<=500 or not 1<=self.concurrency<=100:raise ValueError("invalid capacity")
        if not 0<=self.delay_ms<=1000 or not 1<=self.runs<=100:raise ValueError("invalid budget")
        if not 0<=self.failure_every<=self.agents:raise ValueError("invalid failures")
        if self.graph not in ("independent","chain","fanout"):raise ValueError("invalid graph")

def make_mesh(c):
    nodes=[]
    for i in range(c.agents):
        depends=() if i==0 or c.graph=="independent" else ((f"agent-{i-1}",) if c.graph=="chain" else ("agent-0",))
        async def execute(inputs,objective,index=i):
            await asyncio.sleep(c.delay_ms/1000)
            if c.failure_every and (index+1)%c.failure_every==0:raise ValueError("synthetic_failure")
            return objective
        nodes.append(AsyncAgent(f"agent-{i}",execute,depends))
    return AsyncMesh(nodes,concurrency=c.concurrency,timeout_seconds=5)

def benchmark(c:BenchmarkConfig):
    mesh=make_mesh(c)
    samples=[];passed=failed=blocked=completed=0
    tracemalloc.start()
    try:
        for _ in range(c.runs):
            start=perf_counter()
            result=asyncio.run(mesh.run("synthetic benchmark"))
            samples.append((perf_counter()-start)*1000)
            passed+=int(result.accepted)
            failed+=sum(e["status"]=="failed" for e in result.trace)
            blocked+=sum(e["status"]=="blocked" for e in result.trace)
            completed+=sum(e["status"]=="completed" for e in result.trace)
        peak=tracemalloc.get_traced_memory()[1]
    finally:tracemalloc.stop()
    total=c.runs*c.agents
    return {"schema_version":1,"workload":asdict(c),"metrics":{
      "p50_ms":round(percentile(samples,50),3),
      "p95_ms":round(percentile(samples,95),3),
      "run_success_rate":passed/c.runs,
      "node_failure_rate":failed/total,
      "blocked_rate":blocked/total,
      "completed_rate":completed/total,
      "peak_tracemalloc_bytes":peak,
      "samples_ms":[round(v,3) for v in samples]},
      "limitations":"Synthetic in-process asyncio workload; memory is Python allocations, not full RSS."}

def compare(current,baseline,threshold=.25):
    if current["workload"]!=baseline["workload"]:raise ValueError("workloads differ")
    previous=baseline["metrics"]["p95_ms"]
    if previous<=0 or not 0<=threshold<=10:raise ValueError("invalid comparison")
    delta=(current["metrics"]["p95_ms"]-previous)/previous
    return {"p95_delta_pct":round(delta*100,2),"regression":delta>threshold,"threshold_pct":100*threshold}
