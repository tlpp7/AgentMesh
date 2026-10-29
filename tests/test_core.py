import pytest
from agentmesh import Agent, Constraint, Mesh, Task

def test_default_agents():
    result = Mesh().run(Task("Build a pipeline"))
    assert result.accepted
    assert result.attempts == 1
    assert len(result.trace) == 4

def test_exhausted_retries():
    result = Mesh(max_attempts=2).run(
        Task("Build", [Constraint("never", lambda text: False)])
    )
    assert not result.accepted
    assert result.attempts == 2
    assert result.violations == ["never"]
    assert result.trace[-1]["supervisor"] == "rejected"

def test_retry_until_valid():
    state = {"calls": 0}
    def worker(text, task):
        state["calls"] += 1
        return "ready" if state["calls"] == 2 else "pending"
    result = Mesh([Agent("worker", worker)], max_attempts=3).run(
        Task("Start", [Constraint("ready", lambda text: text == "ready")])
    )
    assert result.accepted and result.attempts == 2

def test_invalid_parameters():
    with pytest.raises(ValueError):
        Mesh(max_attempts=0)
    with pytest.raises(ValueError):
        Mesh(agents=[])
    with pytest.raises(ValueError):
        Mesh().run(Task("   "))
