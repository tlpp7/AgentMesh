"""Optional PostgreSQL connection factory. Credentials are never logged."""
import os

def connect_postgres(dsn=None):
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError("Install pip install -e '.[postgres]'") from exc
    url=dsn or os.environ.get("AGENTMESH_DATABASE_URL")
    if not url:raise ValueError("AGENTMESH_DATABASE_URL required")
    return psycopg.connect(url,connect_timeout=5)
