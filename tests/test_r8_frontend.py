from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_r8_telemetry_panel_exists():
    api=(ROOT/"apps/web-v2/src/api.ts").read_text()
    ui=(ROOT/"apps/web-v2/src/main.tsx").read_text()
    assert "/api/v2/telemetry?limit=30" in api
    assert 'id="telemetry"' in ui
    assert "refreshTelemetry" in ui
