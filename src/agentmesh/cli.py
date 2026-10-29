"""AgentMesh command-line interface."""
import argparse
import json
from .core import Constraint, Mesh, Task

def main() -> None:
    parser = argparse.ArgumentParser(description="Run an offline multi-agent demo")
    parser.add_argument("objective", help="Task objective")
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--json", action="store_true", help="Print the execution trace")
    args = parser.parse_args()
    task = Task(args.objective, constraints=[Constraint("nonempty", lambda s: bool(s.strip()))])
    result = Mesh(max_attempts=args.max_attempts).run(task)
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False) if args.json else result.output)
    if not result.accepted:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
