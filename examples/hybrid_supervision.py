"""Run both hybrid branches without external model providers."""
import json
from agentmesh.hybrid import run_hybrid

text=run_hybrid(objective="Design resilient agents",requirements=["Review:","Plan:"])
numeric=run_hybrid(matrix=[[1,0.3],[0.2,1]],target=[2,1],gain=0.5,
                   lower=[-5,-5],upper=[5,5])
print(json.dumps({"text":text.to_dict(),"numeric":numeric.to_dict()},indent=2))
