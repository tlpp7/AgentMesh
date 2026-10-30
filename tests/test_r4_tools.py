import pytest
from agentmesh.mcp_server import invoke_tool
from agentmesh.tool_supervisor import run_tool_plan

def test_issue_review_read_only():
    result=invoke_tool("review_issue",{"issue":{"number":7,"title":"Add test coverage","body":"Test errors"}})
    assert result["status"]=="ok"
    assert result["result"]["automated_merge"] is False

def test_trace_evaluation():
    result=invoke_tool("evaluate_trace",{"trace":[
        {"status":"completed"},{"status":"failed"},{"status":"blocked"}]})
    assert result["result"]["total"]==3
    assert result["result"]["success_rate"]==pytest.approx(1/3)

def test_unknown_tool_refused():
    with pytest.raises(ValueError):
        invoke_tool("shell",{"command":"echo secret"})

def test_bounded_plan_denies_unlisted_tools():
    output=run_tool_plan([
        {"tool":"evaluate_trace","arguments":{"trace":[{"status":"completed"}]}},
        {"tool":"github_write","arguments":{"repo":"other/repo"}}])
    assert output["executed"]==1
    assert output["steps"][1]["status"]=="denied"

def test_invalid_inputs_and_limits():
    with pytest.raises(ValueError):
        invoke_tool("review_issue",{"issue":"not an object"})
    with pytest.raises(ValueError):
        invoke_tool("evaluate_trace",{"trace":[{}]*501})
    with pytest.raises(ValueError):
        run_tool_plan([{"tool":"evaluate_trace","arguments":{}}]*9)
