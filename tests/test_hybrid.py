import pytest
from agentmesh.hybrid import run_text,run_numeric,run_hybrid

def test_text_hybrid():
    r=run_text("plan",["Review:","Plan:"])
    assert r.accepted and r.output["attempts"]==2
    assert r.diagnostics["fraction_passing"]==1

def test_numeric_converges():
    r=run_numeric([[1,0.3],[0.2,1]],[2,1],gain=0.5)
    assert r.accepted
    assert r.output["residual"]<1e-7
    assert r.diagnostics["contraction_sufficient"]

def test_numeric_impossible_box():
    r=run_numeric([[1,0],[0,1]],[2,0],lower=[0,0],upper=[1,1],max_steps=25)
    assert not r.accepted
    assert r.diagnostics["feasibility"]=="proven_infeasible"

def test_numeric_not_converged():
    r=run_numeric([[1,0],[0,1]],[2,1],gain=0.1,max_steps=1)
    assert not r.accepted

def test_dispatch():
    assert run_hybrid(objective="build",requirements=["Plan:"]).mode=="text"
    assert run_hybrid(matrix=[[1]],target=[1]).mode=="numeric"

def test_reject_mixed_and_bad_inputs():
    with pytest.raises(ValueError): run_numeric([[1,2]],[1])
    with pytest.raises(ValueError): run_numeric([[1]],[1],lower=[0])
    with pytest.raises(ValueError): run_text("x",["Plan:","Plan:"])
    with pytest.raises(ValueError): run_hybrid()
