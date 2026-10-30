"""Q01 reproducible, evidence-only baseline: unknown is never a pass."""
import argparse,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CHECKS={"python_tests":[sys.executable,"-m","pytest","-q"],"python_compile":[sys.executable,"-m","compileall","-q","src","apps/api"],"frontend_typecheck":["npm","run","typecheck"],"frontend_build":["npm","run","build"]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--execute",action="store_true")
    p.add_argument("--output",default=".local/quality-baseline.json")
    args=p.parse_args()
    data={"schema_version":1,"timestamp":datetime.now(timezone.utc).isoformat(),"checks":{},"standards":{"wcag_2_2_aa":"UNKNOWN","owasp_asvs_5":"UNKNOWN","owasp_api_top10":"UNKNOWN","core_web_vitals":"UNKNOWN","slsa_1_2":"UNKNOWN"}}
    for name,command in CHECKS.items():
        result={"status":"UNKNOWN","reason":"not_executed"}
        if args.execute:
            try:
                r=subprocess.run(command,cwd=ROOT/"apps/web-v2" if name.startswith("frontend") else ROOT,capture_output=True,text=True,timeout=180)
                result={"status":"PASS" if r.returncode==0 else "FAIL","exit_code":r.returncode,"output_tail":(r.stdout+"\n"+r.stderr)[-3000:]}
            except (OSError,subprocess.TimeoutExpired) as exc:
                result={"status":"FAIL","reason":type(exc).__name__}
        data["checks"][name]=result
    target=ROOT/args.output
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(data,indent=2),encoding="utf-8")
    print(json.dumps({"file":str(target),"checks":{k:v["status"] for k,v in data["checks"].items()}}))
    if args.execute and any(v["status"]=="FAIL" for v in data["checks"].values()):return 1
    return 0
if __name__=="__main__":raise SystemExit(main())
