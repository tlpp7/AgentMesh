"""Adaptive API contract tests."""
import json
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import pytest
from server import Handler

@pytest.fixture
def endpoint():
    server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
    thread=Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/api/run"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)

def post(endpoint,data):
    request=Request(endpoint,method="POST",
        headers={"Content-Type":"application/json"},
        data=json.dumps(data).encode())
    with urlopen(request,timeout=4) as response:
        return json.load(response)

def test_adaptive_recovers(endpoint):
    result=post(endpoint,{"mode":"adaptive","objective":"Build a pipeline",
         "requirements":["Review:","Plan:"],"attempts":3})
    assert result["accepted"]
    assert result["attempts"]==2
    assert result["metrics"]["revision_calls"]==1
    assert result["trace"][0]["violations"]==["required:0","required:1"]

def test_adaptive_budget_rejection(endpoint):
    result=post(endpoint,{"mode":"adaptive","objective":"Build a pipeline",
         "requirements":["Review:"],"attempts":1})
    assert not result["accepted"]
    assert result["violations"]==["required:0"]

def test_adaptive_validation(endpoint):
    request=Request(endpoint,method="POST",headers={"Content-Type":"application/json"},
       data=json.dumps({"mode":"adaptive","objective":"ok","requirements":"invalid"}).encode())
    with pytest.raises(HTTPError) as err:
        urlopen(request,timeout=4)
    assert err.value.code==400
