import json
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen,Request
from urllib.error import HTTPError
import pytest
from server import Handler

@pytest.fixture
def endpoint():
    server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
    thread=Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)

def post(endpoint,body):
    req=Request(endpoint+"/api/run",data=json.dumps(body).encode(),headers={"Content-Type":"application/json"},method="POST")
    with urlopen(req,timeout=3) as response:
        return json.load(response)

def test_health(endpoint):
    with urlopen(endpoint+"/api/health") as response:
        assert json.load(response)["status"]=="ok"

def test_index(endpoint):
    with urlopen(endpoint+"/") as response:
        html = response.read().decode("utf-8")
        assert "<title>AgentMesh — Control plane</title>" in html
        assert 'data-panel="overview"' in html

def test_agent_pipeline(endpoint):
    result=post(endpoint,{"mode":"agents","objective":"test"})
    assert result["accepted"]
    assert result["metrics"]["agent_calls"]==3

def test_inverse_pipeline(endpoint):
    result=post(endpoint,{"mode":"inverse","gain":0.5})
    assert len(result["inverse"])==2
    assert len(result["feedback"]["history"])>=1

def test_invalid_request(endpoint):
    with pytest.raises(HTTPError) as err:
        post(endpoint,{"mode":"agents","objective":""})
    assert err.value.code==400


def test_rejected_constraint_is_explicit(endpoint):
    result=post(endpoint,{"mode":"agents","objective":"Analyse","contains":"expression introuvable","attempts":3})
    assert result["accepted"] is False
    assert result["attempts"]==3
    assert result["metrics"]["agent_calls"]==9
    assert result["metrics"]["constraint_checks"]==6
    assert result["violations"]==["contains:expression introuvable"]
