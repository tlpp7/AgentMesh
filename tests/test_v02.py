import json
import pytest
from agentmesh import Agent, Constraint, Mesh, Task, contains, min_length, max_length, nonempty
from agentmesh.telemetry import append_result, summarize

def test_metrics_and_trace():
    result = Mesh().run(Task("Build a pipeline", [nonempty()]))
    assert result.accepted
    assert result.metrics["agent_calls"] == 3
    assert result.metrics["constraint_checks"] == 1
    assert result.metrics["duration_ms"] >= 0
    assert all("duration_ms" in x for x in result.trace if "agent" in x)

def test_composable_constraints():
    result = Mesh().run(Task("plan", [nonempty(), contains("review"), min_length(20), max_length(1000)]))
    assert result.accepted and not result.violations

def test_rejections_and_metrics():
    result = Mesh(max_attempts=2).run(Task("test", [contains("absent-needle")]))
    assert not result.accepted
    assert result.metrics["agent_calls"] == 6
    assert result.trace[-1]["supervisor"] == "rejected"

def test_jsonl_roundtrip(tmp_path):
    file = tmp_path / "logs" / "runs.jsonl"
    append_result(file, Mesh().run(Task("example")))
    append_result(file, Mesh(max_attempts=1).run(Task("example", [contains("impossible")])) )
    data = summarize(file)
    assert data["runs"] == 2
    assert data["accepted"] == 1
    assert data["rejected"] == 1
    assert data["acceptance_rate"] == 0.5
    assert len(file.read_text().splitlines()) == 2

def test_validation():
    with pytest.raises(ValueError):
        min_length(-1)
    with pytest.raises(ValueError):
        max_length(-1)
    with pytest.raises(ValueError):
        contains("")
    with pytest.raises(ValueError):
        Mesh([Agent("same", lambda s,t:s), Agent("same", lambda s,t:s)])
    with pytest.raises(ValueError):
        Mesh().run(Task("ok", [nonempty(), nonempty()]))

def test_exception_trace_preserves_error_type():
    def fail(text, task):
        raise RuntimeError("failure")
    with pytest.raises(RuntimeError, match="failure"):
        Mesh([Agent("broken", fail)]).run(Task("test"))
