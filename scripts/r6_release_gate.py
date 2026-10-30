"""R6 release gate. Defaults to safe local checks; no deployment action."""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CHECKS=[
    ("syntax",[sys.executable,"-m","compileall","-q","src","apps","scripts","server.py"]),
    ("pytest",[sys.executable,"-m","pytest","-q"]),
    ("doctor",[sys.executable,"scripts/r0_doctor.py","--strict"]),
]
def run_gate(include_frontend=False):
    checks=list(CHECKS)
    if include_frontend:
        checks.append(("react_build",["npm","run","build"]))
    results=[]
    for name,cmd in checks:
        cwd=ROOT/"apps/web-v2" if name=="react_build" else ROOT
        try:
            completed=subprocess.run(cmd,cwd=cwd,stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,text=True,timeout=180,check=False)
            results.append({"name":name,"ok":completed.returncode==0,
                "exit_code":completed.returncode,"output_tail":completed.stdout[-2500:]})
        except (OSError,subprocess.TimeoutExpired) as error:
            results.append({"name":name,"ok":False,"error_type":type(error).__name__})
    return {"schema_version":1,"generated_utc":datetime.now(timezone.utc).isoformat(),
        "checks":results,"ready":all(result["ok"] for result in results),
        "scope":"Local validation only. No production readiness certification."}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frontend",action="store_true")
    p.add_argument("--output",default="r6-release-report.json")
    args=p.parse_args()
    report=run_gate(args.frontend)
    Path(args.output).write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"ready":report["ready"],
        "checks":[{"name":x["name"],"ok":x["ok"]} for x in report["checks"]]},indent=2))
    if not report["ready"]:raise SystemExit(1)
if __name__=="__main__":main()
