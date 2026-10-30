"""R2 frontend integration contract checks without requiring Node in Python CI."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"apps"/"web-v2"

def test_frontend_has_api_and_dashboard():
    client=(ROOT/"src/api.ts").read_text()
    ui=(ROOT/"src/main.tsx").read_text()
    assert '"/api/v2/run"' in client
    assert '"/api/health"' in client
    assert "ReactFlow" in ui
    assert "await execute(" in ui
    assert "type RunResult" in ui
    assert "Exporter JSON" in ui

def test_dev_proxy_avoids_public_cors():
    config=(ROOT/"vite.config.ts").read_text()
    assert '"/api"' in config
    assert "127.0.0.1:8001" in config

def test_no_baked_in_secrets():
    for file in (ROOT/"src/api.ts",ROOT/"src/main.tsx"):
        source=file.read_text()
        assert "sk-proj-" not in source
        assert "localStorage" not in source
        assert "sessionStorage" not in source
