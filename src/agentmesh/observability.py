"""Normalize execution traces into useful, bounded diagnostics.

No semantic judgement: root causes are evidence-based only.
Does not copy agent outputs into diagnostic events by default.
"""
from collections import Counter

def analyze_run(payload: dict, *, max_events: int = 500) -> dict:
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dict")
    if not 1 <= max_events <= 10000:
        raise ValueError("invalid event limit")
    trace = payload.get("trace")
    mode = payload.get("mode", "agents")
    if not isinstance(trace, list):
        trace = payload.get("output", {}).get("trace", []) if isinstance(payload.get("output"), dict) else []
    if not isinstance(trace, list):
        trace = []
    events = []
    for seq, raw in enumerate(trace[:max_events]):
        if not isinstance(raw, dict):
            continue
        agent = raw.get("agent") or ("supervisor" if "supervisor" in raw else "reviser" if "decision" in raw else "unknown")
        status = raw.get("status") or raw.get("decision") or raw.get("supervisor") or "unknown"
        violations = raw.get("violations", [])
        if not isinstance(violations, list):
            violations = []
        events.append({
            "sequence": seq + 1,
            "agent": str(agent),
            "attempt": raw.get("attempt"),
            "status": str(status),
            "duration_ms": raw.get("duration_ms"),
            "error_type": raw.get("error_type"),
            "violations": [str(x) for x in violations][:30],
        })
    # Numeric algorithms often expose iteration history rather than agent traces.
    numerical = payload.get("feedback") if isinstance(payload.get("feedback"), dict) else None
    if numerical is None and isinstance(payload.get("output"), dict):
        o = payload["output"]
        if "residual" in o:
            numerical = {"converged": payload.get("diagnostics", {}).get("converged"),
                         "iterations": o.get("iterations"), "residual": o.get("residual")}
    failures = [e for e in events if e["status"] in ("error", "reject", "rejected") or e["violations"]]
    causes = []
    for e in failures:
        cause = "exception" if e["status"] == "error" else "constraint_violation"
        causes.append({"agent": e["agent"], "attempt": e["attempt"], "category": cause,
                       "error_type": e["error_type"], "violations": e["violations"]})
    if numerical and numerical.get("converged") is False:
        causes.append({"agent": "numeric_controller", "attempt": None,
                       "category": "iteration_budget_or_tolerance", "error_type": None,
                       "violations": []})
    # No assertion of blame from the last agent in a chain.
    counts = dict(Counter(e["agent"] for e in events))
    return {
        "schema_version": 1,
        "mode": mode,
        "accepted": payload.get("accepted"),
        "event_count": len(events),
        "truncated": len(trace) > max_events,
        "agents": counts,
        "failure_count": len(causes),
        "suspected_causes": causes[:50],
        "events": events,
        "numeric": numerical,
        "disclaimer": "Observed failure points only; no causal or semantic proof.",
    }
