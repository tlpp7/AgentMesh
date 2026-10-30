# R5 — Optimization and security regression gates

R5 keeps the original Python backend, FastAPI R1, React R2, R3 event journal, and R4 MCP tools intact.

## Performance test suite

The R5 runner executes four bounded, synthetic AsyncMesh configurations: independent agents, fanout, chain, and dependency failures. It captures latency p50/p95, outcome rates and Python allocation peaks.

```bash
cd /workspaces/AgentMesh
source .venv/bin/activate
python -m pip install -e '.[dev,api]' httpx
python -m pytest tests/test_r5_validation.py -v
python -m pytest -q
python scripts/r5_validation.py --output r5-baseline.json
python scripts/r5_validation.py --baseline r5-baseline.json --output r5-current.json --threshold 0.25 --fail-on-regression
```

The baseline should be generated on the same machine, interpreter and environment as subsequent samples. Comparison rejects workload changes and reports whether the environment metadata matches. A single result is *not* proof of optimization.

## Security invariants

- Exposing the legacy server remotely continues to require explicit opt-in plus a sufficiently long token.
- Unknown R4 tool names cannot execute through the tool supervisor.
- These tests are regression checks, not penetration testing or an independent security audit.

## Operational limits

- Real LLM latency/cost, external MCP traffic, database contention and full OS RSS are not measured.
- No Rust/Zig optimization is automatically activated. Profile first; replace only proven CPU bottlenecks.
- R5 does **not** establish production readiness: rate limiting, identity management, HTTPS, secrets rotation, hardened deployments, dependency audits and end-to-end browser coverage remain required.
- R5 scripts have no network side effects and do not modify the existing API.

## R5 acceptance

Run Python tests and benchmark commands in Codespaces, compare repeated baselines, verify Node build and npm audit separately, and inspect any failing checks before attempting a deployment.
