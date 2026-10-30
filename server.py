"""AgentMesh local HTTP API and frontend, using only Python stdlib."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import url2pathname
from ipaddress import ip_address
import json
import os
import hmac
import time

ROOT = Path(__file__).resolve().parent
TOKEN = os.getenv("AGENTMESH_API_TOKEN", "")
DB_PATH = os.getenv("AGENTMESH_DB_PATH", "")
def store():
    if not DB_PATH: return None
    from agentmesh.storage import RunStore
    return RunStore(DB_PATH)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT / "web"),**kwargs)
    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        super().end_headers()
    def authorized(self):
        return not TOKEN or hmac.compare_digest(self.headers.get("Authorization",""),"Bearer "+TOKEN)
    def run_response(self,mode,payload):
        from agentmesh.observability import analyze_run
        payload["observability"] = analyze_run({**payload, "mode": mode})
        database=store()
        if database:
            accepted=payload.get("accepted",payload.get("feedback",{}).get("converged",False))
            payload["run_id"]=database.append(mode,accepted,payload)
        return self.respond(200,payload)
    def respond(self, code, data):
        raw=json.dumps(data,ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(raw)))
        self.send_header("Cache-Control","no-store")
        self.end_headers()
        self.wfile.write(raw)
    def do_GET(self):
        route=urlparse(self.path).path
        if route=="/api/health":
            return self.respond(200,{"status":"ok","version":"0.6.0","persistence":bool(DB_PATH),"auth_required":bool(TOKEN)})
        if route.startswith("/api/") and not self.authorized():
            return self.respond(401,{"error":"unauthorized"})
        if route=="/api/events":
            db=store()
            if not db: return self.respond(404,{"error":"persistence_disabled"})
            self.send_response(200)
            self.send_header("Content-Type","text/event-stream; charset=utf-8")
            self.send_header("Cache-Control","no-cache")
            self.send_header("X-Accel-Buffering","no")
            self.end_headers()
            last=""
            try:
                for _ in range(12):
                    entries=db.list(limit=1)
                    newest=entries[0]["id"] if entries else ""
                    if newest!=last:
                        payload=json.dumps({"latest":entries[0] if entries else None},ensure_ascii=False)
                        self.wfile.write(("event: runs\ndata: "+payload+"\n\n").encode())
                        self.wfile.flush()
                        last=newest
                    else:
                        self.wfile.write(b": heartbeat\n\n")
                        self.wfile.flush()
                    time.sleep(1)
            except (ConnectionError,OSError):
                return
            return
        if route=="/api/observability":
            db=store()
            if not db:
                return self.respond(200,{"enabled":False,"runs":[]})
            runs=db.list(limit=30)
            summaries=[]
            for run in runs:
                payload=db.get(run["id"])
                if payload is None: continue
                view=payload.get("observability")
                if view is None:
                    from agentmesh.observability import analyze_run
                    view=analyze_run({**payload,"mode":run["mode"]})
                summaries.append({"id":run["id"],"created":run["created"],
                                  "accepted":run["accepted"],"failure_count":view["failure_count"],
                                  "event_count":view["event_count"],"mode":run["mode"]})
            return self.respond(200,{"enabled":True,"runs":summaries})
        if route=="/api/runs":
            db=store()
            return self.respond(200,{"runs":db.list() if db else [],"enabled":bool(db)})
        if route.startswith("/api/runs/"):
            db=store()
            if not db: return self.respond(404,{"error":"persistence_disabled"})
            value=db.get(route[len("/api/runs/"):])
            return self.respond(200,value) if value is not None else self.respond(404,{"error":"not_found"})
        if route=="/api/architecture":
            return self.respond(200,{"nodes":["Input","Analyzer","Proposer","Critic","Constraints","Supervisor","Result"],"edges":[["Input","Analyzer"],["Analyzer","Proposer"],["Proposer","Critic"],["Critic","Constraints"],["Constraints","Supervisor"],["Supervisor","Result"]]})
        if route=="/": self.path="/index.html"
        return super().do_GET()
    def do_POST(self):
        if urlparse(self.path).path!="/api/run":
            return self.respond(404,{"error":"not_found"})
        if not self.authorized(): return self.respond(401,{"error":"unauthorized"})
        origin=self.headers.get("Origin")
        if origin:
            from urllib.parse import urlsplit
            parsed=urlsplit(origin)
            if parsed.scheme not in ("http","https") or parsed.netloc != self.headers.get("Host"):
                return self.respond(403,{"error":"cross_origin_request_denied"})
        try:
            size=int(self.headers.get("Content-Length","0"))
            if not 1<=size<=65536:
                return self.respond(413,{"error":"invalid_payload_size"})
            data=json.loads(self.rfile.read(size))
            if not isinstance(data,dict):
                raise ValueError("object expected")
            mode=data.get("mode","agents")
            if mode=="gain_search":
                from agentmesh.gain_control import compare_gains
                from dataclasses import asdict
                matrix=data.get("matrix",[[1,.3],[.2,1]])
                target=data.get("target",[2,1])
                if not isinstance(matrix,list) or not matrix or len(matrix)>10 or any(not isinstance(row,list) or len(row)!=len(matrix) for row in matrix) or not isinstance(target,list) or len(target)!=len(matrix):
                    raise ValueError("invalid square matrix or target")
                tolerance=float(data.get("tolerance",1e-7))
                max_steps=int(data.get("max_steps",100))
                if not 1<=max_steps<=1000: raise ValueError("invalid budget")
                gains=data.get("gains",[0.1,0.25,0.5,0.75,1.0])
                if not isinstance(gains,list) or not 1<=len(gains)<=20:
                    raise ValueError("invalid gain list")
                result=compare_gains(matrix,[0.0]*len(target),target,gains=gains,max_steps=max_steps,tolerance=tolerance)
                return self.respond(200,{"best":asdict(result["best"]),"candidates":[asdict(c) for c in result["candidates"]]})
            if mode=="diagnostics":
                from agentmesh.diagnostics import conditioning,residual_report
                a=data.get("matrix",[[1,.3],[.2,1]])
                value={"conditioning":conditioning(a)}
                if "state" in data and "target" in data:
                    value["residual"]=residual_report(a,data["state"],data["target"])
                return self.respond(200,value)
            if mode=="agents":
                from agentmesh.core import Mesh,Task
                from agentmesh.constraints import nonempty,contains
                objective=data.get("objective","")
                if not isinstance(objective,str) or not 0<len(objective.strip())<=5000:
                    raise ValueError("objective must be nonempty and at most 5000 characters")
                attempts=int(data.get("attempts",3))
                if not 1<=attempts<=10:
                    raise ValueError("attempts must be between 1 and 10")
                constraints=[nonempty()]
                term=data.get("contains","")
                if term:
                    if not isinstance(term,str): raise ValueError("contains must be a string")
                    constraints.append(contains(term))
                try:
                    result=Mesh(max_attempts=attempts).run(Task(objective,constraints))
                except Exception as exc:
                    trace=getattr(exc,"agentmesh_trace",None)
                    if trace is None:
                        raise
                    return self.run_response(mode,{"accepted":False,"output":"",
                        "attempts":trace[-1].get("attempt",1) if trace else 1,
                        "trace":trace,"violations":[],
                        "error":{"type":type(exc).__name__,"message":"Agent execution failed"},
                        "metrics":{"agent_calls":sum(e.get("status")=="ok" for e in trace if "agent" in e),
                                   "constraint_checks":0}})
                return self.run_response(mode,result.to_dict())
            if mode=="hybrid":
                from agentmesh.hybrid import run_hybrid
                branch=data.get("branch","text")
                if branch=="text":
                    objective=data.get("objective","")
                    requirements=data.get("requirements",["Review:","Plan:"])
                    attempts=int(data.get("attempts",4))
                    if not isinstance(objective,str) or len(objective)>5000 or not 1<=attempts<=10:
                        raise ValueError("invalid objective or attempts")
                    return self.run_response(mode,run_hybrid(objective=objective,requirements=requirements,
                                    max_attempts=attempts).to_dict())
                if branch=="numeric":
                    matrix=data.get("matrix",[[1,.3],[.2,1]])
                    target=data.get("target",[2,1])
                    return self.run_response(mode,run_hybrid(matrix=matrix,target=target,
                        gain=float(data.get("gain",.5)),
                        max_steps=min(1000,int(data.get("max_steps",100))),
                        lower=data.get("lower"),upper=data.get("upper")).to_dict())
                raise ValueError("unknown hybrid branch")
            if mode=="adaptive":
                from agentmesh.adaptive import AdaptiveMesh, Rule
                objective=data.get("objective","")
                if not isinstance(objective,str) or not 0<len(objective.strip())<=5000:
                    raise ValueError("objective must be nonempty and at most 5000 characters")
                attempts=int(data.get("attempts",4))
                if not 1<=attempts<=10:
                    raise ValueError("attempts must be between 1 and 10")
                needs=data.get("requirements",["Review:","Plan:"])
                if not isinstance(needs,list) or len(needs)>10 or any(not isinstance(v,str) or not v or len(v)>120 for v in needs):
                    raise ValueError("requirements must be a list of short nonempty strings")
                # Safe local illustrative revision: append only missing markers.
                def produce(goal):
                    return "Analysis: " + goal
                def revise(goal,feedback):
                    output=feedback.previous_output
                    for name in feedback.violations:
                        marker=needs[int(name.split(":")[1])]
                        output += "\n" + marker + " completed locally."
                    return output
                rules=[Rule(f"required:{i}",lambda text,marker=marker: marker in text)
                       for i,marker in enumerate(needs)]
                result=AdaptiveMesh(produce,revise,rules,max_attempts=attempts).run(objective)
                return self.run_response(mode,result.to_dict())
            if mode=="inverse":
                from agentmesh.inverse import inverse_linear,reflexive_feedback
                from agentmesh.micro import cross_sensitivity,interval_feasibility,feedback_stability
                a=data.get("matrix",[[1,.3],[.2,1]])
                y=data.get("target",[2,1])
                if not isinstance(a,list) or not isinstance(y,list) or len(a)>10 or len(y)>10 or any(not isinstance(row,list) or len(row)>10 for row in a):
                    raise ValueError("matrix dimensions exceed limits")
                gain=float(data.get("gain",.5))
                x=inverse_linear(a,y,ridge=.001)
                feedback=reflexive_feedback(a,[0]*len(x),y,gain=gain,max_steps=50)
                return self.run_response(mode,{"inverse":x,"feedback":{"converged":feedback.converged,"iterations":feedback.iterations,"residual":feedback.residual,"history":feedback.history,"state":feedback.state},"sensitivity":cross_sensitivity(a,[.1]*len(x)),"feasibility":interval_feasibility(a,[-5]*len(x),[5]*len(x),y),"stability":feedback_stability(a,gain).__dict__})
            raise ValueError("unknown mode")
        except (TypeError,ValueError,KeyError,OverflowError,ZeroDivisionError) as exc:
            return self.respond(400,{"error":type(exc).__name__,"message":str(exc)})
        except Exception:
            return self.respond(500,{"error":"internal_error"})

def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--host",default="127.0.0.1")
    parser.add_argument("--port",type=int,default=8000)
    args=parser.parse_args()
    print(f"AgentMesh UI: http://{args.host}:{args.port}",flush=True)
    ThreadingHTTPServer((args.host,args.port),Handler).serve_forever()

if __name__=="__main__": main()
