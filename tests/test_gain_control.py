import pytest
from agentmesh.gain_control import compare_gains

def test_adaptive_faster_than_small_gain():
    r=compare_gains([[1,.3],[.2,1]],[0,0],[2,1],gains=[.1,.5,1],max_steps=100)
    assert r["best"].converged
    assert r["best"].iterations < r["candidates"][0].iterations

def test_budget_exhaustion_is_not_success():
    r=compare_gains([[1]],[0],[1],gains=[.1],max_steps=1)
    assert not r["best"].converged

def test_invalid_gain():
    with pytest.raises(ValueError): compare_gains([[1]],[0],[1],gains=[0])
