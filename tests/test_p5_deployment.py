import pytest
from agentmesh.deployment import DeploymentConfig,loopback
from agentmesh.storage import RunStore

def test_loopback_defaults():
    assert loopback("127.0.0.1")
    assert loopback("::1")
    assert not loopback("0.0.0.0")

def test_remote_requires_explicit_opt_in():
    with pytest.raises(ValueError): DeploymentConfig("0.0.0.0","","",False).validate()
    with pytest.raises(ValueError): DeploymentConfig("0.0.0.0","short","",True).validate()
    assert DeploymentConfig("0.0.0.0","x"*40,"",True).validate()

def test_local_without_token():
    assert DeploymentConfig("127.0.0.1","","").validate()

def test_sqlite_backup_and_retention(tmp_path):
    db=RunStore(tmp_path/"runs.db")
    for i in range(5):
        db.append("agents",i%2==0,{"index":i})
    backup=tmp_path/"backup.db"
    assert db.backup(backup)==str(backup.resolve())
    restored=RunStore(backup)
    assert len(restored.list())==5
    assert db.prune(2)==3
    assert len(db.list())==2
    assert len(restored.list())==5

def test_sqlite_retention_invalid(tmp_path):
    db=RunStore(tmp_path/"runs.db")
    with pytest.raises(ValueError):db.prune(0)
    with pytest.raises(ValueError):db.backup(tmp_path/"runs.db")
