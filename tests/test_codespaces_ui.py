"""Regression checks for Codespaces private API connection."""
from pathlib import Path
from agentmesh.deployment import DeploymentConfig

ROOT=Path(__file__).resolve().parents[1]

def test_private_codespaces_binding():
    config=DeploymentConfig("0.0.0.0","x"*40,"",True)
    assert config.validate()

def test_browser_token_ui_contract():
    html=(ROOT/"web/index.html").read_text(encoding="utf-8")
    js=(ROOT/"web/app.js").read_text(encoding="utf-8")
    for identifier in ("configureApiToken","apiAuthPanel","apiTokenInput","saveApiToken","clearApiToken","apiTokenNotice"):
        assert 'id="'+identifier+'"' in html
        assert identifier in js
    assert 'window.agentmeshToken=token' in js
    assert 'sessionStorage' not in js and 'localStorage' not in js

def test_api_header_is_conditional():
    js=(ROOT/"web/app.js").read_text(encoding="utf-8")
    assert '"Authorization":"Bearer "+window.agentmeshToken' in js
