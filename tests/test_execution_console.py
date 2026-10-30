from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_execution_console_controls():
    html=(ROOT/"web/index.html").read_text()
    for key in ("traceSearch","traceSort","sortDir","viewNetwork","viewTable","traceCount","traceTableBody","consoleDetail","consoleNetworkPane","consoleTablePane"):
        assert f'id="{key}"' in html

def test_execution_console_client_logic():
    js=(ROOT/"web/app.js").read_text()
    for name in ("function consoleEvents(","function filteredConsoleRows(","function drawConsole(","function consoleView("):
        assert name in js
    assert "escapeHTML(e.agent)" in js
    assert "data-filter-group" in js

def test_typescript_contract_exists():
    ts=(ROOT/"web/types/observability.ts").read_text()
    assert "interface TraceEvent" in ts
    assert "interface Observability" in ts
