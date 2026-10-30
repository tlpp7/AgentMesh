"""R5 reproducible benchmark suite, stored baselines and explicit thresholds.

Synthetic workloads only. No remote model/tool calls.
"""
import json
import math
import platform
from datetime import datetime, timezone
from pathlib import Path
from .performance import BenchmarkConfig, benchmark

SUITES = (
    BenchmarkConfig(agents=20,concurrency=4,delay_ms=2,runs=8,graph="independent"),
    BenchmarkConfig(agents=40,concurrency=8,delay_ms=2,runs=8,graph="fanout"),
    BenchmarkConfig(agents=20,concurrency=4,delay_ms=1,runs=8,graph="chain"),
    BenchmarkConfig(agents=20,concurrency=4,delay_ms=1,runs=8,failure_every=5,graph="chain"),
)

def suite():
    results=[]
    for config in SUITES:
        report=benchmark(config)
        results.append(report)
    return {"schema_version":1,"created":datetime.now(timezone.utc).isoformat(),
            "environment":{"python":platform.python_version(),"system":platform.system(),"machine":platform.machine()},
            "results":results}

def compare_suite(current,baseline,limit=.25):
    if not isinstance(limit,(int,float)) or not math.isfinite(limit) or not 0<=limit<=10:
        raise ValueError("invalid regression threshold")
    if len(current["results"])!=len(baseline["results"]):
        raise ValueError("suite size mismatch")
    checks=[]
    for new,old in zip(current["results"],baseline["results"]):
        if new["workload"]!=old["workload"]:
            raise ValueError("workload mismatch")
        before=old["metrics"]["p95_ms"]
        after=new["metrics"]["p95_ms"]
        if before<=0:raise ValueError("invalid baseline p95")
        delta=(after/before)-1
        checks.append({"workload":new["workload"],"p95_change_pct":round(delta*100,2),
                       "regression":delta>limit,
                       "success_rate_regression":new["metrics"]["run_success_rate"]<old["metrics"]["run_success_rate"]})
    return {"checks":checks,"regressions":sum(c["regression"] or c["success_rate_regression"] for c in checks),
            "threshold_pct":100*limit,"environment_comparable":current["environment"]==baseline["environment"]}
