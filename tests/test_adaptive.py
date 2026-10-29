import pytest
from agentmesh.adaptive import AdaptiveMesh, Rule

def test_reviser_gets_violations_and_recovers():
    seen=[]
    def revise(goal, feedback):
        seen.append(feedback)
        return feedback.previous_output + " Review:"
    result=AdaptiveMesh(lambda goal:"Analysis", revise,
                        [Rule("review",lambda s:"Review:" in s)]).run("test")
    assert result.accepted and result.attempts==2
    assert seen[0].violations==("review",)
    assert result.metrics["revision_calls"]==1

def test_stagnation_ends_early():
    result=AdaptiveMesh(lambda _: "a",lambda goal,fb:"a",
                        [Rule("b",lambda s:"b" in s)],
                        max_attempts=10,stagnation_limit=2).run("test")
    assert not result.accepted and result.attempts==3
    assert result.metrics["stopped_for_stagnation"]

def test_progress_score():
    def revise(goal,fb):
        return "A B" if fb.attempt==2 else "A"
    result=AdaptiveMesh(lambda _: "",revise,
                        [Rule("a",lambda s:"A" in s),Rule("b",lambda s:"B" in s)],
                        max_attempts=3).run("test")
    assert result.accepted and result.metrics["final_score"]==1
    assert result.trace[1]["improvement"]==1

def test_rule_exception_means_violation():
    def fail(_): raise RuntimeError("invalid")
    result=AdaptiveMesh(lambda _:"ok",lambda goal,fb:"ok",
                        [Rule("failure",fail)],max_attempts=1).run("goal")
    assert not result.accepted and result.violations==["failure"]

def test_empty_rules_accept():
    result=AdaptiveMesh(lambda _:"ok",lambda goal,fb:"unexpected",[]).run("goal")
    assert result.accepted and result.attempts==1

def test_invalid_parameters():
    with pytest.raises(ValueError):
        AdaptiveMesh(lambda _:"",lambda a,b:"",[],max_attempts=0)
    with pytest.raises(ValueError):
        AdaptiveMesh(lambda _:"",lambda a,b:"",[Rule("x",lambda _:True),Rule("x",lambda _:False)])
    with pytest.raises(ValueError):
        AdaptiveMesh(lambda _:"",lambda a,b: "",[]).run(" ")
    with pytest.raises(TypeError):
        AdaptiveMesh(None,lambda a,b:"",[])

def test_bad_agent_output():
    with pytest.raises(TypeError):
        AdaptiveMesh(lambda _:None,lambda a,b:"",[]).run("goal")
