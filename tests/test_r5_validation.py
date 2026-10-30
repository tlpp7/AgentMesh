"""R5 performance and security regression tests."""
import math
import pytest
from agentmesh.r5_validation import compare_suite,SUITES
from agentmesh.deployment import DeploymentConfig
from agentmesh.tool_supervisor import run_tool_plan

def sample(workload,p95,success=1):
    return {"workload":workload,"metrics":{"p95_ms":p95,"run_success_rate":success}}

def test_baseline_rules():
    workload={"agents":20,"concurrency":4}
    env={"python":"3.14","system":"Linux","machine":"x86_64"}
    old={"results":[sample(workload,100)],"environment":env}
    new={"results":[sample(workload,130)],"environment":env}
    result=compare_suite(new,old)
    assert result["regressions"]==1
    assert result["environment_comparable"]
    assert result["checks"][0]["p95_change_pct"]==30.0

def test_reject_mismatched_workloads_and_bad_thresholds():
    old={"results":[sample({"agents":20},100)],"environment":{}}
    new={"results":[sample({"agents":30},90)],"environment":{}}
    with pytest.raises(ValueError):compare_suite(new,old)
    for value in (-1,math.inf,math.nan):
        with pytest.raises(ValueError):compare_suite(old,old,value)

def test_success_rate_regression():
    workload={"agents":20}
    old={"results":[sample(workload,100,1)],"environment":{}}
    new={"results":[sample(workload,95,.8)],"environment":{}}
    assert compare_suite(new,old)["regressions"]==1

def test_synthetic_workloads_bounded():
    assert len(SUITES)==4
    assert all(c.agents<=500 and c.runs<=100 for c in SUITES)

def test_remote_binding_fails_closed():
    with pytest.raises(ValueError):
        DeploymentConfig("0.0.0.0","","",True).validate()

def test_unlisted_write_tool_stays_denied():
    output=run_tool_plan([{"tool":"repository_write","arguments":{"branch":"main"}}])
    assert output["executed"]==0
    assert output["steps"][0]["status"]=="denied"
