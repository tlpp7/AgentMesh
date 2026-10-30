"""Guard the agent-centric visualization contract."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_radial_ui_controls():
    html=(ROOT/"web/index.html").read_text()
    for control in ("overviewGraph","agentGraph","replayOverview","replayGraph","pauseReplay","stepReplay","replaySpeed","graphEvent"):
        assert f'id="{control}"' in html

def test_orbital_graph_and_replay():
    js=(ROOT/"web/app.js").read_text()
    for identifier in ("function renderGraph(","function startReplay(","function replayFrame(","function stopReplay(","Math.cos(angle)","Math.sin(angle)","graphEvents(data)"):
        assert identifier in js

def test_visual_feedback_has_reduced_motion():
    css=(ROOT/"web/style.css").read_text()
    assert ".graph-running" in css
    assert "prefers-reduced-motion" in css
