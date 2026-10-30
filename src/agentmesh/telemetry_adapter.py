"""Optional OpenTelemetry tracing adapter; no SDK required for core AgentMesh."""
from contextlib import contextmanager

@contextmanager
def trace_span(name, attributes=None):
    if not isinstance(name,str) or not name:raise ValueError("span name required")
    try:
        from opentelemetry import trace
    except ImportError:
        yield None
        return
    tracer=trace.get_tracer("agentmesh")
    with tracer.start_as_current_span(name) as span:
        for key,value in (attributes or {}).items():
            if isinstance(value,(str,int,float,bool)):
                span.set_attribute(str(key),value)
        yield span
