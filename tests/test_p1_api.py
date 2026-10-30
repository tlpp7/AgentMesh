"""P1 HTTP is explicitly opt-in and must not invoke an API without configuration."""
import json
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import pytest
import server

@pytest.fixture
def endpoint(monkeypatch):
    monkeypatch.delenv("AGENTMESH_ENABLE_LLM",raising=False)
    server.TOKEN=""
    api=ThreadingHTTPServer(("127.0.0.1",0),server.Handler)
    thread=Thread(target=api.serve_forever,daemon=True)
    thread.start()
    try:yield f"http://127.0.0.1:{api.server_port}/api/run"
    finally:
        api.shutdown()
        api.server_close()
        thread.join(timeout=3)

def test_llm_mode_disabled_by_default(endpoint):
    req=Request(endpoint,method="POST",
        headers={"Content-Type":"application/json"},
        data=json.dumps({"mode":"llm","objective":"Do not call network"}).encode())
    with pytest.raises(HTTPError) as exc:
        urlopen(req,timeout=3)
    assert exc.value.code==403
    assert json.load(exc.value)["error"]=="llm_disabled"
