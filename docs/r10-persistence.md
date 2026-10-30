# R10 — Transactional SQLite outbox (incremental)

R10 adds `src/agentmesh/r10_outbox.py` as an **optional** event outbox. The existing SQLite R3 run journal, FastAPI, React, core agents and legacy server are not changed.

## Contract

- `put(stream,kind,payload,event_id=None)`: insert JSON event with UUID key; retries using identical identifiers and payloads are idempotent.
- `pending(limit=50)`: return ordered unacknowledged events, max 500.
- `mark_attempt(event_id)`: increment attempt count for a pending event.
- `acknowledge(event_id)`: mark an event delivered only after the consumer confirms success.
- SQLite transactions persist inserts and state changes across process restarts.

This is an outbox **storage primitive**, not yet a background dispatcher, distributed queue, exactly-once delivery guarantee, PostgreSQL migration or atomic integration with R3 run writes. Those require further steps and integration tests before R10 can be called complete for production.

## Codespaces

```bash
cd /workspaces/AgentMesh
git pull --ff-only origin main
source .venv/bin/activate
python -m pytest tests/test_r10_outbox.py -v
python -m pytest -q
```

## Example

```python
from agentmesh.r10_outbox import DurableOutbox
outbox=DurableOutbox(".local/r10-events.db")
event_id=outbox.put("run:123","completed",{"accepted":True})
print(outbox.pending())
outbox.mark_attempt(event_id)
outbox.acknowledge(event_id)
```

Keep database paths private; don't use a test database to hold production events.
