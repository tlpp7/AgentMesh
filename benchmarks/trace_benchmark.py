"""Local non-comparative observability microbenchmark, stdlib only."""
import json
import statistics
from time import perf_counter
from agentmesh.observability import analyze_run

def run(iterations=30,events=1000):
    trace=[{"agent":f"agent-{i%10}","attempt":1,"status":"ok","duration_ms":0.02} for i in range(events)]
    payload={"accepted":True,"trace":trace}
    samples=[]
    for _ in range(iterations):
        before=perf_counter()
        result=analyze_run(payload,max_events=events)
        json.dumps(result)
        samples.append((perf_counter()-before)*1000)
    return {"iterations":iterations,"events":events,"median_ms":round(statistics.median(samples),3),
            "min_ms":round(min(samples),3),"max_ms":round(max(samples),3)}

if __name__=="__main__":
    print(json.dumps(run(),indent=2))
