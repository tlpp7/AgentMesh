import pytest
from agentmesh.event_journal import EventJournal

def test_atomic_record_and_replay(tmp_path):
    journal=EventJournal(tmp_path/"events.db")
    result={"accepted":True,"trace":[
        {"agent":"analyzer","status":"completed"},
        {"agent":"proposer","status":"completed"}]}
    run_id=journal.record(result)
    assert journal.get_run(run_id)==result
    assert journal.list_runs()[0]["id"]==run_id
    assert [e["sequence"] for e in journal.events(run_id)]==[1,2]
    assert [e["sequence"] for e in journal.events(run_id,after=1)]==[2]

def test_transaction_rolls_back_on_bad_event(tmp_path):
    journal=EventJournal(tmp_path/"events.db")
    with pytest.raises(ValueError):
        journal.record({"accepted":True,"trace":[{"status":"completed"},None]})
    assert journal.list_runs()==[]

def test_bounds_and_missing(tmp_path):
    journal=EventJournal(tmp_path/"events.db")
    assert journal.get_run("missing") is None
    assert journal.events("missing")==[]
    with pytest.raises(ValueError):journal.events("x",after=-1)
    with pytest.raises(ValueError):journal.list_runs(101)

def test_r3_fastapi_persistence(tmp_path,monkeypatch):
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient
    from apps.api.main import create_app
    monkeypatch.setenv("AGENTMESH_DB_PATH",str(tmp_path/"api.db"))
    monkeypatch.setenv("AGENTMESH_API_TOKEN","r"*40)
    client=TestClient(create_app())
    authorized={"Authorization":"Bearer "+"r"*40}
    created=client.post("/api/v2/run",json={"objective":"Analyze system"},headers=authorized)
    assert created.status_code==200
    run_id=created.json()["run_id"]
    assert client.get("/api/v2/runs").status_code==401
    listing=client.get("/api/v2/runs",headers=authorized)
    assert listing.status_code==200 and listing.json()["runs"][0]["id"]==run_id
    assert client.get("/api/v2/runs/"+run_id,headers=authorized).json()["accepted"]
    replay=client.get("/api/v2/runs/"+run_id+"/events?after=0",headers=authorized)
    assert replay.status_code==200
    events=replay.json()["events"]
    assert [e["sequence"] for e in events]==list(range(1,len(events)+1))
    assert client.get("/api/v2/runs/missing",headers=authorized).status_code==404
