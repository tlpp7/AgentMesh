"""P4 synthetic load test CLI."""
import argparse
import json
from pathlib import Path
from agentmesh.performance import BenchmarkConfig,benchmark,compare

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--agents",type=int,default=20)
    p.add_argument("--concurrency",type=int,default=4)
    p.add_argument("--delay-ms",type=float,default=2.0)
    p.add_argument("--runs",type=int,default=8)
    p.add_argument("--failure-every",type=int,default=0)
    p.add_argument("--graph",choices=["independent","chain","fanout"],default="independent")
    p.add_argument("--output",default="p4-report.json")
    p.add_argument("--baseline")
    p.add_argument("--threshold",type=float,default=.25)
    p.add_argument("--fail-on-regression",action="store_true")
    args=p.parse_args()
    c=BenchmarkConfig(args.agents,args.concurrency,args.delay_ms,args.runs,args.failure_every,args.graph)
    report=benchmark(c)
    if args.baseline:
        old=json.loads(Path(args.baseline).read_text())
        report["comparison"]=compare(report,old,args.threshold)
    Path(args.output).write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    if args.fail_on_regression and report.get("comparison",{}).get("regression"):
        raise SystemExit(2)

if __name__=="__main__":main()
