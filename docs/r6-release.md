# R6 — Release validation and reversible rollout

R6 is a **deployment-readiness gate**, not an automatic production deploy. It preserves the original application on port 8000 and the optional FastAPI/React services on ports 8001/5173.

## Codespaces gate

```bash
cd /workspaces/AgentMesh
git pull --ff-only origin main
source .venv/bin/activate
python -m pip install -e '.[dev,api]' httpx
python -m pytest tests/test_r6_release_gate.py -v
python scripts/r6_release_gate.py --output r6-release-report.json
cd apps/web-v2 && npm install && npm run build
cd ../..
python scripts/r6_release_gate.py --frontend --output r6-with-frontend.json
```

The gate checks syntax, Python tests, environment doctor and optionally the React production build. It returns exit code 1 if any check fails; it **never deploys**.

## Safe deployment sequence

1. Keep the original port 8000 service available as a rollback route.
2. Back up the R3 SQLite database with the P5 maintenance script before any migration.
3. Run the R6 gate and retain the report.
4. Start FastAPI on 127.0.0.1:8001 and React on 127.0.0.1:5173, with forwarded ports set to **Private**.
5. Validate /api/health, authenticated /api/v2/run, run listing and replay; test React manually.
6. Only then test a separate HTTPS-enabled deployment with an identity layer, operational alerts and rate limits.
7. If checks fail, stop the optional services and continue on the legacy dashboard (port 8000). Restore a verified SQLite backup only if required; do not overwrite current data without review.

## Limitations

- R6 has no infrastructure credentials, public endpoint exposure, automated GitHub release, rollback automation or hardening certification.
- The report may include truncated test output. Review it for sensitive data before publishing as a CI artifact.
- Load tests, end-to-end browser checks, database migration drills and a security audit remain acceptance items for production.
