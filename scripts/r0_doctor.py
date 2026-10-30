"""R0 non-invasive environment and compatibility diagnostic."""
import argparse, importlib.util, json, platform, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def probe():
    modules=["pytest","fastapi","uvicorn","pydantic","psycopg","opentelemetry","mcp","openai"]
    deps={name:importlib.util.find_spec(name) is not None for name in modules}
    paths={"legacy_server":ROOT.joinpath("server.py").is_file(),
           "legacy_frontend":ROOT.joinpath("web/index.html").is_file(),
           "async_engine":ROOT.joinpath("src/agentmesh/async_engine.py").is_file(),
           "optional_api":ROOT.joinpath("apps/api/main.py").is_file(),
           "optional_react":ROOT.joinpath("apps/web-v2/package.json").is_file()}
    result={"schema_version":1,"python":platform.python_version(),
            "python_supported":sys.version_info >= (3,10),
            "legacy_paths":paths,"optional_packages":deps,
            "checks":{"core_unchanged":all(paths[k] for k in ("legacy_server","legacy_frontend","async_engine")),
                      "optional_api_present":paths["optional_api"],
                      "optional_web_present":paths["optional_react"]}}
    result["ready"]=result["python_supported"] and result["checks"]["core_unchanged"]
    return result
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output")
    p.add_argument("--strict",action="store_true")
    a=p.parse_args()
    report=probe()
    raw=json.dumps(report,indent=2,ensure_ascii=False)
    print(raw)
    if a.output:Path(a.output).write_text(raw+"\n",encoding="utf-8")
    if a.strict and not report["ready"]:raise SystemExit(1)
if __name__=="__main__":main()
