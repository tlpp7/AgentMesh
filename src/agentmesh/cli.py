"""AgentMesh command-line interface."""
import argparse
import json
from .constraints import contains, nonempty
from .core import Mesh, Task
from .telemetry import append_result, summarize

def main() -> None:
    parser = argparse.ArgumentParser(description="Local multi-agent orchestration")
    parser.add_argument("objective", nargs="?", help="Task objective")
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--contains", help="Require a phrase in the result")
    parser.add_argument("--json", action="store_true", help="Print structured run data")
    parser.add_argument("--trace-file", help="Append execution as a JSONL record locally")
    parser.add_argument("--report", help="Summarize a previously recorded JSONL trace file")
    args = parser.parse_args()
    if args.report:
        print(json.dumps(summarize(args.report), indent=2))
        return
    if not args.objective:
        parser.error("objective is required unless --report is provided")
    constraints = [nonempty()]
    if args.contains:
        constraints.append(contains(args.contains))
    result = Mesh(max_attempts=args.max_attempts).run(Task(args.objective, constraints))
    if args.trace_file:
        append_result(args.trace_file, result)
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False) if args.json else result.output)
    if not result.accepted:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
