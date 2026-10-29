"""Constraint-guided adaptive supervisor, offline and deterministic."""
from dataclasses import dataclass, field
from time import perf_counter
from typing import Callable, Sequence

@dataclass(frozen=True)
class Feedback:
    attempt: int
    violations: tuple[str, ...]
    previous_output: str
    previous_score: float

@dataclass(frozen=True)
class Rule:
    name: str
    check: Callable[[str], bool]

@dataclass
class AdaptiveResult:
    accepted: bool
    output: str
    attempts: int
    violations: list[str] = field(default_factory=list)
    trace: list[dict] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)

    def to_dict(self):
        return {"accepted": self.accepted, "output": self.output,
                "attempts": self.attempts, "violations": self.violations,
                "trace": self.trace, "metrics": self.metrics}

class AdaptiveMesh:
    """Run a producer once, then bounded revisions with explicit feedback.

    The reviser MUST be supplied; no claim of autonomous reasoning is implied.
    An improvement is a reduction in failed rule count, not semantic quality.
    """
    def __init__(self, producer: Callable[[str], str],
                 reviser: Callable[[str, Feedback], str],
                 rules: Sequence[Rule], max_attempts: int = 4,
                 stagnation_limit: int = 2):
        if not callable(producer) or not callable(reviser):
            raise TypeError("producer and reviser must be callable")
        if not 1 <= max_attempts <= 100 or stagnation_limit < 1:
            raise ValueError("invalid attempt or stagnation budget")
        self.rules = tuple(rules)
        if len({r.name for r in self.rules}) != len(self.rules):
            raise ValueError("rule names must be unique")
        self.producer, self.reviser = producer, reviser
        self.max_attempts, self.stagnation_limit = max_attempts, stagnation_limit

    def run(self, objective: str) -> AdaptiveResult:
        if not isinstance(objective, str) or not objective.strip():
            raise ValueError("objective must be a nonempty string")
        start = perf_counter()
        trace, previous = [], ""
        violations = []
        score = 0.0
        stale = 0
        for attempt in range(1, self.max_attempts + 1):
            feedback = Feedback(attempt, tuple(violations), previous, score)
            output = (self.producer(objective) if attempt == 1
                      else self.reviser(objective, feedback))
            if not isinstance(output, str):
                raise TypeError("agent must return a string")
            violations = []
            for rule in self.rules:
                try:
                    passed = bool(rule.check(output))
                except Exception:
                    passed = False
                if not passed:
                    violations.append(rule.name)
            new_score = (len(self.rules)-len(violations))/len(self.rules) if self.rules else 1.0
            improvement = new_score - score if attempt > 1 else 0.0
            stale = stale + 1 if attempt > 1 and improvement <= 0 else 0
            accepted = not violations
            stop = accepted or attempt == self.max_attempts or stale >= self.stagnation_limit
            trace.append({"attempt": attempt, "output": output,
                          "violations": list(violations), "score": new_score,
                          "improvement": improvement, "stagnation": stale,
                          "decision": "accept" if accepted else
                          ("reject" if stop else "revise")})
            previous, score = output, new_score
            if stop:
                return AdaptiveResult(
                    accepted, output, attempt, list(violations), trace,
                    {"duration_ms": round((perf_counter()-start)*1000, 3),
                     "constraint_checks": attempt*len(self.rules),
                     "revision_calls": attempt-1, "final_score": score,
                     "stopped_for_stagnation": not accepted and stale >= self.stagnation_limit})
        raise RuntimeError("unreachable")
