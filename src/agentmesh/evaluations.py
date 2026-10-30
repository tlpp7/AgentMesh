"""Deterministic run-outcome statistics, not semantic correctness."""
from collections import Counter
from dataclasses import dataclass

@dataclass(frozen=True)
class Evaluation:
    passed: int
    failed: int
    blocked: int
    total: int

    @property
    def success_rate(self) -> float:
        return self.passed/self.total if self.total else 0.0

    def as_dict(self) -> dict:
        return {"passed":self.passed,"failed":self.failed,"blocked":self.blocked,
                "total":self.total,"success_rate":self.success_rate}

def evaluate_trace(trace) -> Evaluation:
    counts=Counter(event.get("status") for event in trace if isinstance(event,dict))
    passed=counts["completed"]+counts["ok"]
    failed=counts["failed"]+counts["error"]
    blocked=counts["blocked"]
    return Evaluation(passed,failed,blocked,passed+failed+blocked)
