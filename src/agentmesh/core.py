"""Small, deterministic multi-agent execution engine."""
from dataclasses import dataclass, field
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

    def to_dict(self) -> dict:
        return {
            "accepted": self.accepted,
            "output": self.output,
            "attempts": self.attempts,
            "trace": self.trace,
            "violations": self.violations,
        }

class Mesh:
    def __init__(self, agents: Sequence[Agent] | None = None, max_attempts: int = 3):
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        from .demo import default_agents
        self.agents = list(agents) if agents is not None else default_agents()
        if not self.agents:
            raise ValueError("at least one agent is required")
        self.max_attempts = max_attempts

    def run(self, task: Task) -> RunResult:
        if not task.objective.strip():
            raise ValueError("task objective must not be empty")
        trace: list[dict] = []
        violations: list[str] = []
        output = ""
        for attempt in range(1, self.max_attempts + 1):
            output = task.objective
            for agent in self.agents:
                output = agent.execute(output, task)
                if not isinstance(output, str):
                    raise TypeError(f"agent {agent.name} must return a string")
                trace.append({"attempt": attempt, "agent": agent.name, "output": output})
            violations = []
            for constraint in task.constraints:
                try:
                    passed = bool(constraint.predicate(output))
                except Exception:
                    passed = False
                if not passed:
                    violations.append(constraint.name)
            trace.append({"attempt": attempt, "supervisor": "accepted" if not violations else "retry", "violations": list(violations)})
            if not violations:
                return RunResult(True, output, attempt, trace, [])
        trace[-1]["supervisor"] = "rejected"
        return RunResult(False, output, self.max_attempts, trace, violations)
