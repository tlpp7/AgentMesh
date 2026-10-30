import asyncio
import pytest
from agentmesh.extensions import ExtensionRegistry,Extension
from agentmesh.events import EventBus
from agentmesh.evaluations import evaluate_trace

def test_extensions_are_explicit():
    registry=ExtensionRegistry()
    registry.register(Extension("sample","compute",lambda value:value*2))
    assert registry.create("compute","sample",value=3)==6
    with pytest.raises(ValueError):registry.register(Extension("sample","compute",lambda:0))

def test_bounded_events():
    bus=EventBus(2);q=bus.subscribe()
    for i in range(3):bus.publish(bus.new_event("r","agent","completed",i+1))
    assert q.qsize()==2
    assert q.get_nowait().sequence==2
    bus.unsubscribe(q)

def test_evaluations():
    result=evaluate_trace([{"status":"completed"},{"status":"failed"},{"status":"blocked"}])
    assert result.total==3
    assert result.success_rate==pytest.approx(1/3)
