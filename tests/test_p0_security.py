import json
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import Request, urlopen
from urllib.error import HTTPError

import pytest
from server import Handler
from agentmesh.contracts import Event, RunEnvelope

@pytest.fixture
def endpoint():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=3)

def test_security_headers(endpoint):
    with urlopen(endpoint + "/") as response:
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]

def test_post_rejects_cross_origin(endpoint):
    request=Request(endpoint+"/api/run", method="POST",
                    data=json.dumps({"mode":"agents","objective":"safe"}).encode(),
                    headers={"Content-Type":"application/json","Origin":"https://evil.example"})
    with pytest.raises(HTTPError) as result:
        urlopen(request,timeout=3)
    assert result.value.code == 403

def test_post_allows_same_origin(endpoint):
    request=Request(endpoint+"/api/run", method="POST",
                    data=json.dumps({"mode":"agents","objective":"safe"}).encode(),
                    headers={"Content-Type":"application/json","Origin":endpoint})
    with urlopen(request,timeout=3) as result:
        assert json.load(result)["accepted"]

def test_typed_contract_roundtrip():
    event=Event(1,"analyzer","ok",attempt=1,duration_ms=0.2)
    packet=RunEnvelope("r1","agents",True,(event,))
    assert packet.to_dict()["events"][0]["agent"] == "analyzer"

@pytest.mark.parametrize("kwargs",[
    {"sequence":0,"agent":"a","status":"ok"},
    {"sequence":1,"agent":"","status":"ok"},
    {"sequence":1,"agent":"a","status":"ok","duration_ms":-1},
])
def test_contract_rejects_invalid(kwargs):
    with pytest.raises(ValueError):
        Event(**kwargs)
