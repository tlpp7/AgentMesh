"""R15 offline feasibility demonstration. No network or model API needed."""
import json
from agentmesh.constraint_solver import Bound,solve_constraints

def main():
    scenarios={
        "feasible":[Bound("lower","x","lower",1),Bound("upper","x","upper",3)],
        "contradiction":[Bound("lower","x","lower",5),Bound("upper","x","upper",2)],
        "coupled":[Bound("demand","x","lower",2),Bound("capacity","y","upper",5),
                   Bound("flow","x","difference",1,"y")],
    }
    print(json.dumps({name:solve_constraints(rules) for name,rules in scenarios.items()},indent=2))
if __name__=="__main__":main()
