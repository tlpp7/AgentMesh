"""Deterministic, bounded multi-agent orchestration with structured telemetry."""
from dataclasses import dataclass, field
from time import perf_counter
from typing import Callable, Sequence

@dataclass(frozen=True)
class Constraint:
    name: str
    predicate: Callable[[str], bool]

@dataclass(frozen=True)
class Task:
    objective: str
    constraints: Sequence[Constraint] = ()

@dataclass(frozen=True)
class Agent:
    name: str
    execute: Callable[[str, Task], str]

@dataclass
class RunResult:
    accepted: bool
    output: str
    attempts: int
    trace: list[dict] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "accepted": self.accepted,
            "output": self.output,
            "attempts": self.attempts,
            "trace": self.trace,
            "violations": self.violations,
            "metrics": self.metrics,
        }

class Mesh:
    def __init__(self, agents: Sequence[Agent] | None = None, max_attempts: int = 3):
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        from .demo import default_agents
        self.agents = list(agents) if agents is not None else default_agents()
        if not self.agents:
            raise ValueError("at least one agent is required")
        if len(set(agent.name for agent in self.agents)) != len(self.agents):
            raise ValueError("agent names must be unique")
        self.max_attempts = max_attempts

    def run(self, task: Task) -> RunResult:
        if not task.objective.strip():
            raise ValueError("task objective must not be empty")
        if len(set(c.name for c in task.constraints)) != len(task.constraints):
            raise ValueError("constraint names must be unique")
        started = perf_counter()
        trace: list[dict] = []
        violations: list[str] = []
        output = ""
        agent_calls = 0
        for attempt in range(1, self.max_attempts + 1):
            output = task.objective
            for agent in self.agents:
                before = perf_counter()
                try:
                    output = agent.execute(output, task)
                except Exception as exc:
                    trace.append({"attempt": attempt, "agent": agent.name, "status": "error",
                                  "error_type": type(exc).__name__,
                                  "duration_ms": round((perf_counter() - before) * 1000, 3)})
                    raise
                if not isinstance(output, str):
                    raise TypeError(f"agent {agent.name} must return a string")
                agent_calls += 1
                trace.append({"attempt": attempt, "agent": agent.name, "status": "ok",
                              "output": output,
                              "duration_ms": round((perf_counter() - before) * 1000, 3)})
            violations = []
            for constraint in task.constraints:
                try:
                    passed = bool(constraint.predicate(output))
                except Exception:
                    passed = False
                if not passed:
                    violations.append(constraint.name)
            accepted = not violations
            trace.append({"attempt": attempt, "supervisor": "accepted" if accepted else
                         ("rejected" if attempt == self.max_attempts else "retry"),
                         "violations": list(violations)})
            if accepted:
                return RunResult(True, output, attempt, trace, [],
                                 {"duration_ms": round((perf_counter()-started)*1000, 3),
                                  "agent_calls": agent_calls, "constraint_checks": attempt * len(task.constraints)})
        return RunResult(False, output, self.max_attempts, trace, violations,
                         {"duration_ms": round((perf_counter()-started)*1000, 3),
                          "agent_calls": agent_calls,
                          "constraint_checks": self.max_attempts * len(task.constraints)})
