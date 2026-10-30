"""R3 source contract checks; TypeScript build remains a separate gate."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_history_client_and_dashboard():
    client=(ROOT/"apps/web-v2/src/api.ts").read_text()
    ui=(ROOT/"apps/web-v2/src/main.tsx").read_text()
    for path in ("/api/v2/runs?limit=30","/events?after="):
        assert path in client
    for method in ("refreshHistory","inspectRun","getEvents","getRun"):
        assert method in ui
    assert 'id="history"' in ui
    assert "Rejouer" in ui
