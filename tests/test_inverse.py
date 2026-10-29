import pytest
from agentmesh.inverse import inverse_linear, cross_coupling, reflexive_feedback

def test_inverse_identity():
    assert inverse_linear([[1,0],[0,1]],[2,-3],ridge=1e-9)==pytest.approx([2,-3],abs=1e-7)

def test_inverse_illposed():
    x=inverse_linear([[1,1],[2,2]],[3,6],ridge=0.01)
    assert x[0]==pytest.approx(x[1]) and 1.49<x[0]<1.51

def test_inverse_rectangular():
    assert inverse_linear([[1,0],[0,1],[1,1]],[1,2,3],ridge=1e-8)==pytest.approx([1,2],abs=1e-6)

def test_cross_coupling():
    assert cross_coupling([[0,1],[-2,0]],[3,4])==pytest.approx([4,-6])

def test_reflexive_convergence():
    r=reflexive_feedback([[1,0],[0,1]],[0,0],[2,-1],gain=0.5,max_steps=40)
    assert r.converged and r.state==pytest.approx((2,-1),abs=1e-6)

def test_reflexive_nonconvergence():
    r=reflexive_feedback([[1]],[0],[5],max_steps=3,bounds=[(0,1)])
    assert not r.converged and r.state==(1,)

def test_invalid_parameters():
    with pytest.raises(ValueError): inverse_linear([[1]],[1],ridge=0)
    with pytest.raises(ValueError): cross_coupling([[1,2]],[1,2])
    with pytest.raises(ValueError): reflexive_feedback([[1]],[1],[2],gain=0)
