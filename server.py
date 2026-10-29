"""AgentMesh local HTTP API and frontend, using only Python stdlib."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
import json

ROOT = Path(__file__).resolve().parent

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT / "web"),**kwargs)
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
            return self.respond(200,{"status":"ok","version":"0.4.0"})
        if route=="/api/architecture":
            return self.respond(200,{"nodes":["Input","Analyzer","Proposer","Critic","Constraints","Supervisor","Result"],"edges":[["Input","Analyzer"],["Analyzer","Proposer"],["Proposer","Critic"],["Critic","Constraints"],["Constraints","Supervisor"],["Supervisor","Result"]]})
        if route=="/": self.path="/index.html"
        return super().do_GET()
    def do_POST(self):
        if urlparse(self.path).path!="/api/run":
            return self.respond(404,{"error":"not_found"})
        try:
            size=int(self.headers.get("Content-Length","0"))
            if not 1<=size<=65536:
                return self.respond(413,{"error":"invalid_payload_size"})
            data=json.loads(self.rfile.read(size))
            if not isinstance(data,dict):
                raise ValueError("object expected")
            mode=data.get("mode","agents")
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
                return self.respond(200,Mesh(max_attempts=attempts).run(Task(objective,constraints)).to_dict())
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
                return self.respond(200,{"inverse":x,"feedback":{"converged":feedback.converged,"iterations":feedback.iterations,"residual":feedback.residual,"history":feedback.history,"state":feedback.state},"sensitivity":cross_sensitivity(a,[.1]*len(x)),"feasibility":interval_feasibility(a,[-5]*len(x),[5]*len(x),y),"stability":feedback_stability(a,gain).__dict__})
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
