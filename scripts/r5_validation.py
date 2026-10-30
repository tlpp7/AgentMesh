"""R5 suite runner. No baseline is automatically blessed."""
import argparse
import json
from pathlib import Path
from agentmesh.r5_validation import suite, compare_suite

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="r5-results.json")
    parser.add_argument("--baseline")
    parser.add_argument("--threshold",type=float,default=.25)
    parser.add_argument("--fail-on-regression",action="store_true")
    args=parser.parse_args()
    result=suite()
    if args.baseline:
        old=json.loads(Path(args.baseline).read_text(encoding="utf-8"))
        result["comparison"]=compare_suite(result,old,args.threshold)
    Path(args.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"output":args.output,
        "scenarios":len(result["results"]),
        "comparison":result.get("comparison")},indent=2))
    if args.fail_on_regression and result.get("comparison",{}).get("regressions",0):
        raise SystemExit(2)
if __name__=="__main__":main()
