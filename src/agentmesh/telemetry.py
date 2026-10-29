"""Opt-in local JSONL persistence; never sends data over the network."""
import json
from pathlib import Path
from .core import RunResult

def append_result(path: str | Path, result: RunResult) -> None:
    destination = Path(path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")

def summarize(path: str | Path) -> dict:
    total = accepted = attempts = calls = 0
    with Path(path).expanduser().open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            record = json.loads(line)
            total += 1
            accepted += int(bool(record["accepted"]))
            attempts += int(record["attempts"])
            calls += int(record.get("metrics", {}).get("agent_calls", 0))
    return {"runs": total, "accepted": accepted, "rejected": total-accepted,
            "acceptance_rate": accepted / total if total else 0.0,
            "average_attempts": attempts / total if total else 0.0,
            "agent_calls": calls}
