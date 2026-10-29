"""HTTP regression tests for hybrid supervisor."""
import json
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import Request, urlopen
import pytest
from server import Handler

@pytest.fixture
def api():
    srv=ThreadingHTTPServer(("127.0.0.1",0),Handler)
    thread=Thread(target=srv.serve_forever,daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{srv.server_port}/api/run"
    finally:
        srv.shutdown()
        srv.server_close()
        thread.join(timeout=3)

def send(url, data):
    request=Request(url,method="POST",
        headers={"Content-Type":"application/json"},data=json.dumps(data).encode())
    with urlopen(request,timeout=5) as response:
        return json.load(response)

def test_hybrid_text_api(api):
    result=send(api,{"mode":"hybrid","branch":"text","objective":"Analyze a system",
                     "requirements":["Review:","Plan:"]})
    assert result["mode"]=="text"
    assert result["accepted"]
    assert result["output"]["attempts"]==2

def test_hybrid_numeric_api(api):
    result=send(api,{"mode":"hybrid","branch":"numeric",
                     "matrix":[[1,.3],[.2,1]],"target":[2,1],"gain":.5})
    assert result["mode"]=="numeric"
    assert result["accepted"]
    assert result["output"]["residual"]<1e-7

def test_hybrid_infeasible_bounds_api(api):
    result=send(api,{"mode":"hybrid","branch":"numeric",
                     "matrix":[[1,0],[0,1]],"target":[2,0],
                     "lower":[0,0],"upper":[1,1],"gain":.5})
    assert not result["accepted"]
    assert result["diagnostics"]["feasibility"]=="proven_infeasible"
