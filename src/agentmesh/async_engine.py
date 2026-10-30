"""Async DAG orchestrator with bounded concurrency and timeouts."""
import asyncio
from dataclasses import dataclass, field
from time import perf_counter
from typing import Awaitable, Callable
from datetime import datetime, timezone

@dataclass(frozen=True)
class AsyncAgent:
    name: str
    execute: Callable[[dict[str, str], str], Awaitable[str]]
    depends_on: tuple[str, ...] = ()

@dataclass
class GraphResult:
    accepted: bool
    outputs: dict[str, str] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)
    trace: list[dict] = field(default_factory=list)
    duration_ms: float = 0.0

    def to_dict(self) -> dict:
        return {"accepted": self.accepted, "outputs": self.outputs,
                "errors": self.errors, "trace": self.trace,
                "duration_ms": self.duration_ms}

class AsyncMesh:
    def __init__(self, agents: list[AsyncAgent], concurrency: int = 4,
                 timeout_seconds: float = 30.0):
        if concurrency < 1 or timeout_seconds <= 0:
            raise ValueError("concurrency and timeout_seconds must be positive")
        self.agents = {a.name: a for a in agents}
        if len(self.agents) != len(agents) or not agents:
            raise ValueError("agent names must be unique and nonempty")
        for agent in agents:
            if agent.name in agent.depends_on or any(d not in self.agents for d in agent.depends_on):
                raise ValueError("self dependency or unknown dependency")
        remaining = set(self.agents)
        completed = set()
        while remaining:
            ready = {n for n in remaining if set(self.agents[n].depends_on) <= completed}
            if not ready:
                raise ValueError("dependency cycle detected")
            completed.update(ready)
            remaining -= ready
        self.concurrency = concurrency
        self.timeout_seconds = timeout_seconds

    async def run(self, objective: str, on_event: Callable[[dict], None] | None = None) -> GraphResult:
        if not objective.strip():
            raise ValueError("objective must not be empty")
        start = perf_counter()
        semaphore = asyncio.Semaphore(self.concurrency)
        tasks: dict[str, asyncio.Task] = {}
        events: list[dict] = []
        def emit(agent, status, **details):
            event={"sequence":len(events)+1,"agent":agent,"status":status,
                   "timestamp":datetime.now(timezone.utc).isoformat(),**details}
            events.append(event)
            if on_event is not None:
                try: on_event(dict(event))
                except Exception: pass


        async def execute_node(agent: AsyncAgent):
            inputs = {}
            for dependency in agent.depends_on:
                try:
                    inputs[dependency] = await tasks[dependency]
                except (Exception, asyncio.CancelledError) as exc:
                    emit(agent.name,"blocked",dependency=dependency,error_type=type(exc).__name__)
                    raise RuntimeError(f"dependency {dependency} failed") from exc
            async with semaphore:
                before = perf_counter()
                emit(agent.name,"started")
                try:
                    result = await asyncio.wait_for(
                        agent.execute(dict(inputs), objective), self.timeout_seconds)
                    if not isinstance(result, str):
                        raise TypeError("agent must return a string")
                    emit(agent.name,"completed",duration_ms=round((perf_counter()-before)*1000,3))
                    return result
                except BaseException as exc:
                    emit(agent.name,"failed",error_type=type(exc).__name__,duration_ms=round((perf_counter()-before)*1000,3))
                    raise

        remaining = set(self.agents)
        while remaining:
            ready = sorted(n for n in remaining if set(self.agents[n].depends_on) <= set(tasks))
            for name in ready:
                tasks[name] = asyncio.create_task(execute_node(self.agents[name]))
            remaining -= set(ready)
        gathered = await asyncio.gather(*tasks.values(), return_exceptions=True)
        outputs = {}
        errors = {}
        for name, value in zip(tasks, gathered):
            if isinstance(value, BaseException):
                errors[name] = f"{type(value).__name__}: {value}"
            else:
                outputs[name] = value
        return GraphResult(not errors, outputs, errors, events,
                           round((perf_counter()-start)*1000, 3))
