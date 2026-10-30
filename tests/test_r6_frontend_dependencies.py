"""Prevent reintroduction of the unused vulnerable ECharts 5 dependency."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_no_unused_echarts_dependency():
    manifest=json.loads((ROOT/"apps/web-v2/package.json").read_text(encoding="utf-8"))
    assert "echarts" not in manifest.get("dependencies",{})
    assert "echarts" not in manifest.get("devDependencies",{})
