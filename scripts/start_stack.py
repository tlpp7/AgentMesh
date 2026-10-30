"""Start AgentMesh optional API and React Vite UI, local-only by default."""
import argparse
import os
import secrets
import signal
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/".local"/"stack"
def healthy(url):
    try:
        with urlopen(url,timeout=1) as r:return r.status==200
    except Exception:return False
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--no-browser",action="store_true",help="Do not start React dev server")
    args=parser.parse_args()
    STATE.mkdir(parents=True,exist_ok=True)
    if healthy("http://127.0.0.1:8001/api/health"):
        raise SystemExit("Port 8001 already serves an API. Stop it before starting a managed stack.")
    token=os.environ.get("AGENTMESH_API_TOKEN") or secrets.token_urlsafe(32)
    env={**os.environ,"AGENTMESH_API_TOKEN":token,
         "AGENTMESH_DB_PATH":os.environ.get("AGENTMESH_DB_PATH",str(ROOT/".local"/"agentmesh.db")),
         "AGENTMESH_R9_ENFORCE":"1"}
    token_file=STATE/"token"
    token_file.write_text(token,encoding="utf-8")
    token_file.chmod(0o600)
    processes=[]
    def launch(name,command,cwd):
        log=open(STATE/(name+".log"),"a",encoding="utf-8")
        process=subprocess.Popen(command,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,
                                 start_new_session=True)
        log.close()
        (STATE/(name+".pid")).write_text(str(process.pid),encoding="utf-8")
        processes.append(process)
    try:
        launch("api",[sys.executable,"-m","uvicorn","apps.api.main:app","--host","127.0.0.1","--port","8001"],ROOT)
        if not args.no_browser:
            launch("web",["npm","run","dev","--","--host","127.0.0.1"],ROOT/"apps"/"web-v2")
        for _ in range(30):
            if healthy("http://127.0.0.1:8001/api/health"):break
            if processes[0].poll() is not None:raise RuntimeError("API exited; inspect .local/stack/api.log")
            time.sleep(.2)
        else:raise RuntimeError("API did not become healthy")
        print("API ready: http://127.0.0.1:8001/api/health")
        print("React URL: http://127.0.0.1:5173 (when started)")
        print("Token stored locally: .local/stack/token (never commit)")
        print("Stop: python scripts/stop_stack.py")
    except Exception:
        for p in processes:
            if p.poll() is None:os.killpg(p.pid,signal.SIGTERM)
        raise
if __name__=="__main__":main()
