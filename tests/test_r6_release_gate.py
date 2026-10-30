"""R6 gate contract tests do not launch subprocesses."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from r6_release_gate import CHECKS,run_gate

def test_release_gate_has_no_deploy_command():
    commands=" ".join(" ".join(argv) for _,argv in CHECKS)
    assert "pytest" in commands
    assert "compileall" in commands
    assert not any(value in commands for value in ("docker push","kubectl","git push"))

def test_release_gate_reports_failure(monkeypatch):
    import r6_release_gate
    class Failed:
        returncode=1
        stdout="synthetic failure"
    monkeypatch.setattr(r6_release_gate.subprocess,"run",lambda *args,**kwargs:Failed())
    result=run_gate()
    assert result["ready"] is False
    assert all(not x["ok"] for x in result["checks"])

def test_release_gate_reports_success(monkeypatch):
    import r6_release_gate
    class Success:
        returncode=0
        stdout="ok"
    monkeypatch.setattr(r6_release_gate.subprocess,"run",lambda *args,**kwargs:Success())
    assert run_gate()["ready"] is True
