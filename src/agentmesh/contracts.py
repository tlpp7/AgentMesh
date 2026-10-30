"""P0 versioned typed contracts for diagnostic events and result envelopes."""
from dataclasses import dataclass, asdict
from math import isfinite
from typing import Any

SCHEMA_VERSION = 1

@dataclass(frozen=True)
class Event:
    sequence: int
    agent: str
    status: str
    attempt: int | None = None
    duration_ms: float | None = None
    error_type: str | None = None
    violations: tuple[str, ...] = ()

    def __post_init__(self):
        if type(self.sequence) is not int or self.sequence < 1:
            raise ValueError("sequence must be a positive integer")
        if not self.agent.strip() or not self.status.strip():
            raise ValueError("agent and status must not be empty")
        if self.attempt is not None and (type(self.attempt) is not int or self.attempt < 1):
            raise ValueError("attempt must be a positive integer")
        if self.duration_ms is not None and (not isfinite(self.duration_ms) or self.duration_ms < 0):
            raise ValueError("duration_ms must be finite and nonnegative")

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["violations"] = list(self.violations)
        return value

@dataclass(frozen=True)
class RunEnvelope:
    run_id: str
    mode: str
    accepted: bool
    events: tuple[Event, ...]
    schema_version: int = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": self.schema_version, "run_id": self.run_id,
                "mode": self.mode, "accepted": self.accepted,
                "events": [event.to_dict() for event in self.events]}
