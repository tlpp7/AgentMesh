import pytest
from agentmesh.micro import cross_sensitivity, interval_feasibility, feedback_stability, reflexive_adaptation

def test_sensitivity():
    r=cross_sensitivity([[1,2],[3,4]],[1,1],[0,0])
    assert r["effects"]==[3,7] and r["cross_only"]==[2,3]
    assert r["after"]==[3,7]

def test_invalid_sensitivity():
    with pytest.raises(ValueError): cross_sensitivity([[1,2]],[3])

def test_interval_certified_infeasible():
    r=interval_feasibility([[1,-2]],[0,0],[1,1],[9])
    assert r["status"]=="proven_infeasible"
    assert r["envelopes"]==[(-2,1)]

def test_interval_not_proof_of_feasibility():
    r=interval_feasibility([[1,1],[1,1]],[0,0],[1,1],[0,2])
    assert r["status"]=="undetermined"

def test_stability_sufficient():
    s=feedback_stability([[1,0],[0,1]],0.5)
    assert s.sufficient_contraction and s.norm_upper_bound==pytest.approx(.5)

def test_stability_not_sufficient():
    s=feedback_stability([[0,2],[2,0]],1)
    assert not s.sufficient_contraction

def test_adaptation():
    r=reflexive_adaptation([[1]],[0],[1],[.1,.5,1.],steps=15)
    assert r["best"]["residual"]<1e-6 and r["best"]["gain"]==1.

def test_bad_gains():
    with pytest.raises(ValueError): reflexive_adaptation([[1]],[0],[1],[])
