# P0 implementation status (Q01–Q09)

**Status:** delivered baseline safeguards; **not** a WCAG AA or OWASP ASVS certification.

| Lot | Code introduced | Outstanding evidence / major limitation |
| --- | --- | --- |
| Q01 | `scripts/quality_baseline.py` distinguishes PASS, FAIL and UNKNOWN; optional execution | Manual/field audits still UNKNOWN |
| Q02 | Skip link, navigation landmark, main ID, page title and live status | Audit all interactive semantics and focus order |
| Q03 | Focusable button alternative to agent graph, selection announcements | Manual screen-reader validation |
| Q04 | Focus-visible, reduced motion, narrow mobile CSS, 44px agent control | Measure actual contrast, 400% zoom, touch targets across app |
| Q05 | Regression contracts and accessibility review checklist | axe-core browser scan + manual WCAG 2.2 AA test not yet implemented |
| Q06 | Threat model with risk inventory and acceptance criteria | Owner review, severity assignment and reassessment |
| Q07 | Existing RBAC role model reused | Multi-principal identities, authorization for each stored run **missing** |
| Q08 | Secure default response headers; R9 authorization and limiter retained | TLS, edge rate limiting, CSRF/CORS deployment architecture and resource load tests |
| Q09 | Optional per-agent permission check in `run_tool_plan(..., agent=...)` | Calls without agent retain legacy behavior; full MCP enforcement and sandboxing **missing** |

## Run in Codespaces

```bash
cd /workspaces/AgentMesh
git pull --ff-only origin main
source .venv/bin/activate
python -m pip install -e '.[dev,api]' httpx
python -m pytest tests/test_p0_quality_gates.py -v
python -m pytest -q
python scripts/quality_baseline.py --execute --output .local/quality-baseline.json
cd apps/web-v2 && npm install && npm run typecheck && npm run build
```

Only a passing test run can confirm these code changes do not regress existing functionality. Browser and manual accessibility assessments remain separate acceptance gates. Keep forwarded ports private; production deployment is not approved by this change.
