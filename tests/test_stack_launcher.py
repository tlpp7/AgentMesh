"""Offline checks for managed Codespaces launcher; no servers are started."""
from pathlib import Path
import ast

ROOT=Path(__file__).resolve().parents[1]

def test_launch_scripts_compile():
    for name in ("start_stack.py","stop_stack.py"):
        source=(ROOT/"scripts"/name).read_text()
        ast.parse(source)

def test_launch_is_local_and_stores_secret_outside_repository_tracking():
    start=(ROOT/"scripts/start_stack.py").read_text()
    gitignore=(ROOT/".gitignore").read_text()
    assert '--host","127.0.0.1"' in start
    assert "AGENTMESH_R9_ENFORCE" in start
    assert "chmod(0o600)" in start
    assert ".local/" in gitignore

def test_stop_script_checks_process_identity():
    stop=(ROOT/"scripts/stop_stack.py").read_text()
    assert "expected not in command" in stop
    assert "os.killpg" in stop
