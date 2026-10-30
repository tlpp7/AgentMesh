"""Stop only processes identified by the AgentMesh managed stack PID files."""
import os
import signal
from pathlib import Path

STATE=Path(__file__).resolve().parents[1]/".local"/"stack"
for name in ("web","api"):
    file=STATE/(name+".pid")
    if not file.exists():continue
    try:
        pid=int(file.read_text().strip())
        command=(Path("/proc")/str(pid)/"cmdline").read_bytes().replace(b"\x00",b" ").decode(errors="ignore")
        expected="uvicorn apps.api.main:app" if name=="api" else "npm run dev"
        if expected not in command:
            print(name,": PID no longer matches, not stopping")
            continue
        os.killpg(pid,signal.SIGTERM)
        print(name,": stopped")
    except (ValueError,ProcessLookupError,PermissionError,FileNotFoundError):
        print(name,": not running")
    finally:
        file.unlink(missing_ok=True)
