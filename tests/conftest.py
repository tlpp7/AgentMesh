"""Prevent the developer's Codespaces token from leaking into isolated API tests.

Production authentication stays enabled. Tests deliberately start their own HTTP
servers with explicit fixture authentication settings.
"""
import pytest

@pytest.fixture(autouse=True)
def isolate_test_server_auth(monkeypatch):
    import server
    monkeypatch.setattr(server, "TOKEN", "")
