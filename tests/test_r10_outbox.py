from uuid import uuid4
import pytest
from agentmesh.r10_outbox import DurableOutbox

def test_idempotence_ack_and_restart(tmp_path):
    path=tmp_path/"r10.db"
    db=DurableOutbox(path)
    identifier=str(uuid4())
    assert db.put("runs","completed",{"accepted":True},identifier)==identifier
    assert db.put("runs","completed",{"accepted":True},identifier)==identifier
    assert len(db.pending())==1
    assert db.mark_attempt(identifier)
    assert DurableOutbox(path).pending()[0]["attempts"]==1
    assert DurableOutbox(path).acknowledge(identifier)
    assert not DurableOutbox(path).pending()
    assert not db.acknowledge(identifier)

def test_conflicting_idempotency_key_is_rejected(tmp_path):
    db=DurableOutbox(tmp_path/"db.sqlite")
    key=str(uuid4())
    db.put("runs","done",{"value":1},key)
    with pytest.raises(ValueError):
        db.put("runs","done",{"value":2},key)
    assert db.pending()[0]["payload"]=={"value":1}

def test_invalid_inputs(tmp_path):
    db=DurableOutbox(tmp_path/"db.sqlite")
    with pytest.raises(ValueError):db.put("","done",{})
    with pytest.raises(ValueError):db.put("run","done",[])
    with pytest.raises(ValueError):db.put("run","done",{},event_id="bad")
    with pytest.raises(ValueError):db.pending(0)
    with pytest.raises(ValueError):db.put("run","done",{"x":float("nan")})
