"""R4: explicit safe tools exposed through optional MCP stdio transport.

No network access, shell execution or repository writes.
"""
from dataclasses import dataclass
import json
from .integrations import ControlledAdapter, ToolSpec
from .evaluations import evaluate_trace
from .github_workflow import review_plan

def create_tools():
    def validate_issue(args):
        if set(args)!={"issue"} or not isinstance(args["issue"],dict):
            raise ValueError("issue object required")
        return review_plan(args["issue"])
    def evaluate(args):
        if set(args)!={"trace"} or not isinstance(args["trace"],list) or len(args["trace"])>500:
            raise ValueError("trace must contain at most 500 events")
        if any(not isinstance(x,dict) for x in args["trace"]):
            raise ValueError("invalid trace item")
        return evaluate_trace(args["trace"]).as_dict()
    return ControlledAdapter({
        "review_issue":(ToolSpec("review_issue","Prepare a read-only issue plan",False),validate_issue),
        "evaluate_trace":(ToolSpec("evaluate_trace","Count agent outcomes",False),evaluate),
    })

def invoke_tool(name,arguments):
    if not isinstance(arguments,dict):raise ValueError("arguments must be object")
    return create_tools().invoke(name,arguments)

def create_mcp_server():
    """Initialize FastMCP only on explicit request."""
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError("Install pip install -e '.[mcp]'") from exc
    server=FastMCP("AgentMesh R4")
    @server.tool()
    def review_issue(issue:dict)->dict:
        """Generate a review-only plan from supplied issue data."""
        return invoke_tool("review_issue",{"issue":issue})["result"]
    @server.tool()
    def evaluate_trace(trace:list[dict])->dict:
        """Summarize statuses for at most 500 trace events."""
        return invoke_tool("evaluate_trace",{"trace":trace})["result"]
    return server

def main():
    create_mcp_server().run(transport="stdio")

if __name__=="__main__":
    main()
