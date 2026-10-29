import json
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import Request,urlopen
import pytest
from server import Handler

@pytest.fixture
def endpoint():
    server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
    thread=Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        yield "http://127.0.0.1:"+str(server.server_port)+"/api/run"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)

def post(endpoint,payload):
    request=Request(endpoint,data=json.dumps(payload).encode(),method="POST",
                    headers={"Content-Type":"application/json"})
    with urlopen(request,timeout=4) as response:
        return json.load(response)

def test_gain_search_improves_convergence(endpoint):
    result=post(endpoint,{"mode":"gain_search","matrix":[[1,.3],[.2,1]],
        "target":[2,1],"gains":[.1,.5,1.0],"max_steps":100,"tolerance":1e-7})
    assert result["best"]["converged"]
    assert result["best"]["iterations"]<result["candidates"][0]["iterations"]

def test_gain_search_budget_exhaustion(endpoint):
    result=post(endpoint,{"mode":"gain_search","matrix":[[1]],"target":[1],
        "gains":[.1],"max_steps":1,"tolerance":1e-8})
    assert result["best"]["converged"] is False

def test_gain_controls_present():
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    html=(root/"web/index.html").read_text()
    js=(root/"web/app.js").read_text()
    assert 'id="runGainSearch"' in html
    assert 'id="gainTolerance"' in html
    assert '"gain_search"' in js
