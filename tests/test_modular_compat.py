"""Optional modules must not change core imports or require extra dependencies."""
import importlib
import pytest
from agentmesh.core import Mesh,Task
from agentmesh.constraints import nonempty
from agentmesh.extensions import ExtensionRegistry,Extension
from agentmesh.evaluations import evaluate_trace
from agentmesh.events import EventBus

def test_existing_core():
    result=Mesh(max_attempts=1).run(Task("health check",[nonempty()]))
    assert result.accepted

def test_lazy_optional_imports():
    for module in ("agentmesh.postgres_adapter","agentmesh.telemetry_adapter"):
        assert importlib.import_module(module)

def test_evaluator_counts():
    outcome=evaluate_trace([{"status":"completed"},{"status":"failed"},{"status":"blocked"}])
    assert outcome.as_dict()["total"]==3

def test_extension_listing():
    registry=ExtensionRegistry()
    registry.register(Extension("sample","events",lambda:object()))
    assert registry.list()==[{"name":"sample","category":"events"}]

def test_bus_retains_last_events():
    bus=EventBus(max_queue=1)
    queue=bus.subscribe()
    bus.publish(bus.new_event("run","analyzer","started",1))
    bus.publish(bus.new_event("run","analyzer","completed",2))
    assert queue.get_nowait().status=="completed"
    bus.unsubscribe(queue)
