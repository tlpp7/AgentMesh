"""Run the experimental asynchronous DAG engine."""
import asyncio
import json
from agentmesh.async_engine import AsyncAgent, AsyncMesh

async def research(inputs, objective):
    await asyncio.sleep(0.05)
    return f"Research: {objective}"

async def model(inputs, objective):
    await asyncio.sleep(0.05)
    return f"Model: {objective}"

async def supervise(inputs, objective):
    return f"Compared: {inputs['research']} | {inputs['model']}"

async def main():
    agents = [
        AsyncAgent("research", research),
        AsyncAgent("model", model),
        AsyncAgent("supervisor", supervise, ("research", "model")),
    ]
    result = await AsyncMesh(agents, concurrency=2, timeout_seconds=5).run(
        "Evaluate a constraint-based architecture"
    )
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
