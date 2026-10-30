import asyncio
import json
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import Request,urlopen
import pytest
from server import Handler
from agentmesh.live_demo import demo_run

def test_async_lifecycle_events():
    events=[]
    result=asyncio.run(demo_run("hello",events.append,delay_ms=10))
    assert result.accepted
    assert [e["status"] for e in events]==["started","completed"]*3
    assert [e["sequence"] for e in events]==list(range(1,7))
    assert all(e.get("timestamp") for e in events)

def test_async_dependency_failure():
    events=[]
    result=asyncio.run(demo_run("hello",events.append,delay_ms=10,fail_agent="proposer"))
    assert not result.accepted
    assert any(e["agent"]=="proposer" and e["status"]=="failed" for e in events)
    assert any(e["agent"]=="critic" and e["status"]=="blocked" for e in events)

def test_sse_http_events():
    server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
    th=Thread(target=server.serve_forever,daemon=True);th.start()
    try:
        request=Request(f"http://127.0.0.1:{server.server_port}/api/live/run",
          method="POST",headers={"Content-Type":"application/json"},
          data=json.dumps({"objective":"hello","delay_ms":10}).encode())
        with urlopen(request,timeout=5) as response:
            body=response.read().decode()
            assert response.headers["Content-Type"].startswith("text/event-stream")
            assert "event: agent\ndata: " in body
            assert "event: result\ndata: " in body
            assert '"status": "started"' in body
    finally:
        server.shutdown();server.server_close();th.join(timeout=3)

def test_live_ui_contract():
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    html=(root/"web/index.html").read_text()
    js=(root/"web/app.js").read_text()
    assert 'id="runLive"' in html and 'id="liveEvents"' in html
    assert '"/api/live/run"' in js and "liveNodeGraph" in js
