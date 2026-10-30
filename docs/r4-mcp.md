# R4 — Controlled MCP tools and advanced agent supervision

R4 adds a **separate optional MCP stdio server**, allowing MCP clients to use two restricted local tools:

- `review_issue(issue)`: produce a review plan from issue data already supplied by the caller; does not fetch GitHub or change repositories.
- `evaluate_trace(trace)`: count completed, failed and blocked events from no more than 500 supplied trace entries.

The `tool_supervisor.py` module allows only these tools in a bounded 1–8-step plan. Unknown tools are denied. No autonomous network access, shell execution, repository modification or model spending.

## Install and run

```bash
cd /workspaces/AgentMesh
source .venv/bin/activate
python -m pip install -e '.[dev,mcp]'
python -m pytest tests/test_r4_tools.py -v
python -m agentmesh.mcp_server
```

`python -m agentmesh.mcp_server` starts an MCP server over **stdio** for a compatible MCP client. It is not an HTTP website. Configure the client to run the executable using the Codespace's Python environment; do not paste API tokens into MCP tool arguments.

## Further R4 milestones

1. Validate the MCP handshake against a real client.
2. Add separate read-only GitHub fetching through an explicitly scoped connector.
3. Add human approval workflows for any future write actions.
4. Collect invocation latency and redacted audit metadata.
5. Add optional model-assisted tool *proposals*, retaining server-side tool allowlisting.

The original local UI, FastAPI, SQLite journal, deterministic agents, and existing LLM gateway are preserved.
