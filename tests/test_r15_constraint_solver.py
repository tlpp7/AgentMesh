"""R15 feasibility, contradiction and bounded-input tests."""
import pytest
from agentmesh.constraint_solver import Bound,solve_constraints

def test_feasible_interval_witness():
    rules=[Bound("min","x","lower",1),Bound("max","x","upper",5)]
    result=solve_constraints(rules)
    assert result["feasible"]
    assert 1-1e-8<=result["witness"]["x"]<=5+1e-8
    assert result["unsat_core"]==[]

def test_infeasible_interval_minimal_core():
    rules=[Bound("lower","x","lower",3),Bound("upper","x","upper",2),Bound("irrelevant","y","upper",10)]
    result=solve_constraints(rules)
    assert not result["feasible"]
    assert set(result["unsat_core"])=={"lower","upper"}

def test_difference_constraint_witness():
    rules=[Bound("x_min","x","lower",2),Bound("y_max","y","upper",4),
           Bound("x_relative_y","x","difference",1,"y")]
    result=solve_constraints(rules)
    assert result["feasible"]
    x,y=result["witness"]["x"],result["witness"]["y"]
    assert x>=2-1e-8 and y<=4+1e-8 and x-y<=1+1e-8

def test_negative_cycle_detected():
    rules=[Bound("a","x","difference",-1,"y"),Bound("b","y","difference",-1,"x")]
    result=solve_constraints(rules)
    assert not result["feasible"]
    assert set(result["unsat_core"])=={"a","b"}

def test_empty_problem_and_unconstrained_dimension():
    assert solve_constraints([])["feasible"]
    assert solve_constraints([])["witness"]=={}

def test_invalid_inputs():
    with pytest.raises(ValueError):Bound("bad","x","upper",float("nan"))
    with pytest.raises(ValueError):Bound("bad","x","difference",1)
    with pytest.raises(ValueError):solve_constraints([Bound("same","x","upper",1),Bound("same","x","lower",0)])
    with pytest.raises(ValueError):solve_constraints([Bound(str(i),"x","upper",i) for i in range(65)])
    with pytest.raises(ValueError):Bound("name","x","upper",True)

def test_conflict_is_deletion_minimal():
    rules=[Bound("a","x","lower",5),Bound("b","x","upper",3),
           Bound("c","x","upper",10)]
    result=solve_constraints(rules)
    assert not result["feasible"]
    assert all(solve_constraints([r for r in rules if r.name in result["unsat_core"] and r.name!=name])["feasible"]
               for name in result["unsat_core"])
