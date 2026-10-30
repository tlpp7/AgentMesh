# AgentMesh Quality Transformation — Q01–Q24

Baseline date: 2026-10-30. Plan, not a certification or a record of implemented controls.

## Initial estimated ranking (not audited numerical scores)
| Rank | Domain | Estimated score |
|---|---|---:|
| 1 | Accessibility | 28/100 |
| 2 | Production security | 35/100 |
| 3 | Observability | 40/100 |
| 4 | Persistence and resilience | 45/100 |
| 5 | Frontend architecture | 46/100 |
| 6 | CI/CD industrialization | 57/100 |
| 7 | Backend architecture | 70/100 |
| 8 | Automated tests | 72/100 |

## Standards mapping
- WCAG 2.2 AA / ISO/IEC 40500:2025: semantic UX, keyboard, zoom, contrast, screen readers, automated and manual tests.
- WAI-ARIA 1.2: accessible custom interactive graph, alternative text/tree representations.
- OWASP ASVS 5.0.0 and API Security Top 10: threats, authentication, object-level access controls, resource protection, hardening.
- ISO/IEC 25010: reliability, maintainability, security, performance, portability and compatibility.
- Core Web Vitals: field P75 LCP <=2.5s, INP <=200ms, CLS <=0.1.
- SLSA v1.2: supply chain provenance and progressively stronger guarantees.
- OpenTelemetry: context propagation, traces/spans/metrics without secrets.

## Implementation lots (separate reviewed pull requests)
| Lot | Name | Changes | Gate |
|---|---|---|---|
| Q01 | Measured baseline | script, JSON report, CI summary, reproducible environment | metrics collected, absent measurements marked unknown |
| Q02 | Semantic accessibility | landmarks, headings, labels, focus, skip link | axe smoke + keyboard manual checklist |
| Q03 | Graph accessibility | keyboard node selection, alternative hierarchy, screen reader announcements | Playwright keyboard + NVDA/VoiceOver manual |
| Q04 | Responsive and contrast | AA text contrast, 200/400% zoom, reduced motion, touch targets | viewport/zoom and contrast tests |
| Q05 | Accessibility governance | axe CI, traceable WCAG matrix, accessible error cases | no serious/critical automated findings, manual review |
| Q06 | Threat modeling | data flows, trust boundaries, threat register, ASVS traceability | signed-off threats and mitigations |
| Q07 | Identity and permissions | per-principal RBAC, object authorization, session lifecycle | multi-user negative authorization tests |
| Q08 | API protection | validation, quotas, headers, proxy/TLS configurations | OWASP API scenarios blocked |
| Q09 | Agent isolation | tool scopes, allowlists, explicit approvals, budgets | tools denied by default + bypass tests |
| Q10 | OpenTelemetry API | optional SDK, traceparent, spans | correlated traces without sensitive attributes |
| Q11 | Agent tracing | agent/DB span context, trace sampling, run ID | cross-layer correlation verified |
| Q12 | SLO and dashboards | errors, latency, saturation, alerts | alerts and runbooks exercised |
| Q13 | Transactional persistence | R3+R10 atomic outbox, migration plan | crash-consistency tests |
| Q14 | Durable recovery | idempotent consumer, retries, checkpoints | interrupted jobs recover |
| Q15 | Fault injection | stress, concurrency, backup/restore, chaos-like tests | thresholds and RTO/RPO measured |
| Q16 | React modularity | feature components/hooks, API layer, routing | parity E2E unchanged |
| Q17 | Design system | typed tokens, accessible components, themes | visual/accessibility regression |
| Q18 | Frontend efficiency | profiling, splitting, virtualized large graphs | no performance regression |
| Q19 | Core Web Vitals | Lighthouse CI, RUM with consent/privacy, thresholds | P75 field thresholds or explicitly unavailable |
| Q20 | Static quality | Ruff, TS lint/format, type check, API contracts | lint/type gates pass |
| Q21 | Dependency protection | npm lockfile + npm ci, Dependabot, Python audit, CodeQL, secrets | no unreviewed critical findings |
| Q22 | SLSA provenance | SBOM, trusted build attestations, provenance verification | artifact hash and provenance verified |
| Q23 | Test engineering | component, API, browser, contract/coverage traceability | critical user journeys covered |
| Q24 | Release engineering | staging, rollout, rollback, runbooks, release checklist | go/no-go gate exercised |

## Cross-cutting acceptance criteria per PR
1. One bounded domain; no unreviewed rewrites of legacy port 8000 or R1-R15 engines.
2. Tests (including negative-path tests), docs, changelog, migration/rollback guidance.
3. Explicit evidence in CI: logs, artifact and results; do not report compliance solely from code presence.
4. Requirements mapped to stable issue IDs and test IDs (e.g., Q03/WCAG-2.1.1).
5. No plaintext credentials, agent inputs or user data in telemetry.
6. Version-lock dependencies and avoid unsupported breaking upgrades.
7. Manual accessibility checks complement axe; SLSA attainment only when provenance and build-level criteria verified.

## Dependencies and sequence
Q01 first. Then parallel workstreams:
- Accessibility: Q02 -> Q03 -> Q04 -> Q05.
- Security: Q06 -> Q07 -> Q08 -> Q09.
- Observability: Q10 -> Q11 -> Q12.
- Resilience: Q13 -> Q14 -> Q15.
- Frontend: Q16 -> Q17 -> Q18 -> Q19.
- Platform and delivery: Q20 -> Q21 -> Q22 -> Q23 -> Q24.
Security gates and baseline are required before public deployment; Q23 integrates cross-stream checks.

## Concrete Q01 first PR
- Add `scripts/quality_baseline.py` (no external service required) to record Python tests, doctor, npm typecheck/build, deps audit status, accessibility and CWV measurements as unknown unless actually executed.
- Add `docs/quality/evidence-matrix.md` and CI job uploading a timestamped baseline JSON.
- Add tests verifying no invented scores or false pass statuses; failures should be machine-readable.
- Preserve all existing APIs and UI.
- Exit criteria: local and CI baseline output reproducibly, known failures identified and prioritized.

## Links
- https://www.iso.org/standard/91029.html
- https://asvs.owasp.org/
- https://slsa.dev/spec/v1.2/
- https://developers.google.com/search/docs/appearance/core-web-vitals
