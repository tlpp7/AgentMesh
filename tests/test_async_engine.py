import asyncio
import pytest
from agentmesh.async_engine import AsyncAgent, AsyncMesh

def test_dependency_dag():
    async def root(inputs, objective): return objective.upper()
    async def child(inputs, objective): return inputs["root"] + "!"
    mesh = AsyncMesh([AsyncAgent("child", child, ("root",)), AsyncAgent("root", root)])
    result = asyncio.run(mesh.run("hello"))
    assert result.accepted and result.outputs["child"] == "HELLO!"

def test_parallelism():
    async def work(inputs, objective):
        await asyncio.sleep(0.04)
        return objective
    mesh = AsyncMesh([AsyncAgent(str(i), work) for i in range(4)], concurrency=4)
    result = asyncio.run(mesh.run("ok"))
    assert result.accepted and len(result.outputs) == 4
    assert result.duration_ms < 140

def test_cycle():
    async def work(inputs, objective): return "ok"
    with pytest.raises(ValueError, match="cycle"):
        AsyncMesh([AsyncAgent("a", work, ("b",)), AsyncAgent("b", work, ("a",))])

def test_unknown_dependency():
    async def work(inputs, objective): return "ok"
    with pytest.raises(ValueError):
        AsyncMesh([AsyncAgent("a", work, ("missing",))])

def test_timeout_and_propagation():
    async def slow(inputs, objective):
        await asyncio.sleep(0.1)
        return "done"
    async def child(inputs, objective): return "ok"
    result = asyncio.run(AsyncMesh([AsyncAgent("a", slow), AsyncAgent("b", child, ("a",))],
                                   timeout_seconds=0.005).run("x"))
    assert not result.accepted and "a" in result.errors and "b" in result.errors

def test_bad_output():
    async def bad(inputs, objective): return 13
    result = asyncio.run(AsyncMesh([AsyncAgent("bad", bad)]).run("x"))
    assert not result.accepted and "TypeError" in result.errors["bad"]

def test_reject_empty_objective():
    async def work(inputs, objective): return "ok"
    with pytest.raises(ValueError):
        asyncio.run(AsyncMesh([AsyncAgent("a", work)]).run(" "))
