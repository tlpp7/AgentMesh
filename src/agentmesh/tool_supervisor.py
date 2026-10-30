"""Bounded, explicit execution of read-only R4 tools."""
from .mcp_server import invoke_tool
from .security_policy import Policy

ALLOWED=frozenset(("review_issue","evaluate_trace"))

def run_tool_plan(steps, *, agent=None):
    if not isinstance(steps,list) or not 1<=len(steps)<=8:
        raise ValueError("plan size must be 1..8")
    output=[]
    for step in steps:
        if not isinstance(step,dict):
            raise ValueError("step must be object")
        name=step.get("tool")
        args=step.get("arguments")
        if name not in ALLOWED or (agent is not None and not Policy().agent_tool_allowed(agent,name)):
            output.append({"tool":name,"status":"denied"})
        elif not isinstance(args,dict):
            output.append({"tool":name,"status":"invalid"})
        else:
            output.append(invoke_tool(name,args))
    return {"steps":output,"executed":sum(x["status"]=="ok" for x in output)}
