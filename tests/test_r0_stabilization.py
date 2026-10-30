"""R0 verifies backwards compatibility and a non-invasive system doctor."""
import sys
from pathlib import Path
from agentmesh.core import Mesh,Task
from agentmesh.constraints import nonempty
from agentmesh.extensions import ExtensionRegistry
from agentmesh.evaluations import evaluate_trace
from agentmesh.events import EventBus

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from r0_doctor import probe

def test_legacy_core_remains_runnable():
    result=Mesh(max_attempts=1).run(Task("R0 baseline",[nonempty()]))
    assert result.accepted
    assert len(result.trace)>0

def test_optional_modules_do_not_affect_legacy():
    assert ExtensionRegistry().list()==[]
    assert evaluate_trace([{"status":"completed"}]).success_rate==1
    bus=EventBus(2)
    queue=bus.subscribe()
    bus.publish(bus.new_event("r0","agent","started",1))
    assert queue.get_nowait().run_id=="r0"
    bus.unsubscribe(queue)

def test_doctor_schema():
    report=probe()
    assert report["schema_version"]==1
    assert report["ready"] is True
    assert report["checks"]["core_unchanged"] is True
    assert isinstance(report["optional_packages"],dict)
