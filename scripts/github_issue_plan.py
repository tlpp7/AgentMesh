"""P3: inspect a GitHub issue, export a review plan (read-only)."""
import argparse
import json
from pathlib import Path
from agentmesh.github_workflow import GitHubClient,GitHubScope,review_plan

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--repo",required=True)
    parser.add_argument("--issue",required=True,type=int)
    parser.add_argument("--output",default="issue-plan.json")
    args=parser.parse_args()
    output=Path(args.output)
    if not output.name.endswith(".json"):
        parser.error("output must be .json")
    client=GitHubClient(GitHubScope(args.repo))
    plan=review_plan(client.issue(args.issue))
    output.write_text(json.dumps(plan,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("Plan written:",output)

if __name__=="__main__":main()
