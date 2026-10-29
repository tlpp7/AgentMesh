"""Regression checks for the web console and numeric API."""
import json
from pathlib import Path
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import Request, urlopen
import pytest
from server import Handler

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture
def api():
    srv=ThreadingHTTPServer(("127.0.0.1",0), Handler)
    t=Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        yield "http://127.0.0.1:" + str(srv.server_port)
    finally:
        srv.shutdown()
        srv.server_close()
        t.join(timeout=3)

def post(url, body):
    req=Request(url+"/api/run", data=json.dumps(body).encode(),
                headers={"Content-Type":"application/json"}, method="POST")
    with urlopen(req,timeout=5) as response:
        return json.load(response)

def test_four_interactive_sections():
    html=(ROOT/"web/index.html").read_text()
    app=(ROOT/"web/app.js").read_text()
    for name in ("overview","graph","inverse","traces"):
        assert f'data-view="{name}"' in html
        assert f'data-panel="{name}"' in html
    for endpoint in ("/api/health","/api/run","/api/architecture"):
        assert endpoint in app
    for action in ("runAgents","runInverse","clearHistory","downloadJson"):
        assert action in html and action in app

def test_cross_inverse_custom_matrix(api):
    data=post(api,{"mode":"inverse","matrix":[[1,0.3],[0.2,1]],
                   "target":[2,1],"gain":0.5})
    assert data["feedback"]["converged"]
    assert data["feedback"]["residual"]<1e-7
    assert data["stability"]["sufficient_contraction"]
    assert data["feasibility"]["status"]=="undetermined"
    # Regularized inverse and unregularized feedback solve different objectives.
    assert abs(data["inverse"][0]-data["feedback"]["state"][0])>1e-4

def test_architecture_edges_resolve(api):
    with urlopen(api+"/api/architecture") as resp:
        graph=json.load(resp)
    nodes=set(graph["nodes"])
    assert graph["edges"]
    assert all(a in nodes and b in nodes for a,b in graph["edges"])

def test_agents_results_for_traces(api):
    data=post(api,{"mode":"agents","objective":"Analyze a system","contains":"Review:"})
    assert data["accepted"]
    assert data["metrics"]["agent_calls"]==3
    assert any(e.get("supervisor")=="accepted" for e in data["trace"])

def test_adaptive_controls_are_wired():
    html=(ROOT/"web/index.html").read_text()
    script=(ROOT/"web/app.js").read_text()
    assert 'id="runAdaptive"' in html
    assert 'id="adaptiveRequirements"' in html
    assert 'mode:"adaptive"' in script
    assert '"runAdaptive").addEventListener' in script
