import pytest
from agentmesh.github_workflow import GitHubClient,GitHubScope,review_plan

def test_read_issue_and_plan():
    calls=[]
    def transport(method,path,payload):
        calls.append((method,path,payload))
        return {"number":12,"title":"Improve tracing","body":"Add correlation IDs"}
    c=GitHubClient(GitHubScope("tlpp7/AgentMesh"),transport=transport)
    result=review_plan(c.issue(12))
    assert result["title"]=="Improve tracing"
    assert not result["automated_merge"]
    assert calls[0][:2]==("GET","/repos/tlpp7/AgentMesh/issues/12")

def test_draft_only():
    calls=[]
    c=GitHubClient(GitHubScope("tlpp7/AgentMesh"),transport=lambda m,p,v:calls.append((m,p,v)) or {})
    c.draft_pr("Improve tests","Human review needed","agentmesh/p3-tests")
    assert calls[0][2]["draft"] is True

def test_scope_and_branch_rejections():
    with pytest.raises(ValueError):GitHubScope("evil/../../repo")
    c=GitHubClient(GitHubScope("tlpp7/AgentMesh"),transport=lambda *args:{})
    with pytest.raises(ValueError):c.branch("main","0"*40)
    with pytest.raises(ValueError):c.call("GET","/repos/other/repo/issues/1")

def test_no_merge_method():
    assert not hasattr(GitHubClient,"merge")
