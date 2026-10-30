"""P3 GitHub integration: explicit read, branch and draft-PR operations.

Transport is injectable for offline tests. No automatic merge.
"""
from dataclasses import dataclass
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import json
import os
import re

_REPO=re.compile(r"^[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}$")
_BRANCH=re.compile(r"^agentmesh/[a-zA-Z0-9][a-zA-Z0-9_.-]{0,70}$")
_PATH=re.compile(r"^(?!/)(?!.*(?:^|/)\.\.(?:/|$))[\w.\-/]{1,240}$")
class GitHubError(RuntimeError): pass

@dataclass(frozen=True)
class GitHubScope:
    repository: str
    def __post_init__(self):
        if not _REPO.fullmatch(self.repository) or ".." in self.repository:
            raise ValueError("invalid repository")

class GitHubClient:
    def __init__(self, scope: GitHubScope, token=None, transport=None):
        self.scope=scope
        self.token=token if token is not None else os.getenv("AGENTMESH_GITHUB_TOKEN","")
        self.transport=transport
        if not self.token and transport is None:
            raise RuntimeError("AGENTMESH_GITHUB_TOKEN missing")

    def call(self,method,path,payload=None):
        if not path.startswith("/repos/"+self.scope.repository+"/"):
            raise ValueError("path outside repository scope")
        if self.transport is not None:
            return self.transport(method,path,payload)
        request=Request("https://api.github.com"+path,
            data=json.dumps(payload).encode() if payload is not None else None,
            method=method,
            headers={"Authorization":"Bearer "+self.token,"Accept":"application/vnd.github+json",
                     "X-GitHub-Api-Version":"2022-11-28","User-Agent":"AgentMesh-P3",
                     "Content-Type":"application/json"})
        try:
            with urlopen(request,timeout=15) as r:
                return json.load(r)
        except (HTTPError,TimeoutError,OSError) as exc:
            raise GitHubError("github_api_request_failed") from None

    def issue(self,number):
        if type(number) is not int or number<1: raise ValueError("invalid issue number")
        return self.call("GET",f"/repos/{self.scope.repository}/issues/{number}")

    def branch(self,name,base_sha):
        if not _BRANCH.fullmatch(name) or not re.fullmatch("[a-fA-F0-9]{40}",base_sha):
            raise ValueError("invalid branch or SHA")
        return self.call("POST",f"/repos/{self.scope.repository}/git/refs",
                         {"ref":"refs/heads/"+name,"sha":base_sha})

    def draft_pr(self,title,body,head,base="main"):
        if not _BRANCH.fullmatch(head) or not isinstance(title,str) or not 1<=len(title)<=160:
            raise ValueError("invalid pull request")
        if base!= "main": raise ValueError("only main base supported")
        if not isinstance(body,str) or len(body)>10000: raise ValueError("invalid PR body")
        return self.call("POST",f"/repos/{self.scope.repository}/pulls",
                         {"title":title,"body":body,"head":head,"base":base,"draft":True})

def review_plan(issue:dict)->dict:
    """Produce inspectable checklist; deliberately no autonomous code execution."""
    title=str(issue.get("title","")).strip()[:160]
    body=str(issue.get("body") or "")[:3000]
    if not title:raise ValueError("issue title required")
    return {"issue_number":issue.get("number"),"title":title,
            "requirements":body,"steps":["Define acceptance criteria",
                "Create scoped feature branch","Make changes and add tests",
                "Run CI and inspect failures","Open draft PR for human approval"],
            "automated_merge":False}
