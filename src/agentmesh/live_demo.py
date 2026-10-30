"""Bounded demo DAG with real execution events; no LLM calls or remote tools."""
import asyncio
from .async_engine import AsyncAgent, AsyncMesh

def demo_graph(delay_ms=180, fail_agent=""):
    if not 10 <= delay_ms <= 1000:
        raise ValueError("delay_ms must be between 10 and 1000")
    names=["analyzer","proposer","critic"]
    if fail_agent not in ("",*names):
        raise ValueError("unknown fail_agent")
    async def worker(inputs, objective, name):
        await asyncio.sleep(delay_ms/1000)
        if name == fail_agent:
            raise RuntimeError("simulated failure")
        return name+": "+objective[:120]
    def build(name,deps):
        async def execute(inputs, objective):
            return await worker(inputs,objective,name)
        return AsyncAgent(name,execute,depends_on=deps)
    return AsyncMesh([build("analyzer",()),build("proposer",("analyzer",)),
                      build("critic",("proposer",))],timeout_seconds=5)

async def demo_run(objective, callback, *, delay_ms=180, fail_agent=""):
    return await demo_graph(delay_ms,fail_agent).run(objective,on_event=callback)
