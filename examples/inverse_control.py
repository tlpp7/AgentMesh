"""Demonstrate inverse targets, crossed influence and reflexive correction."""
import json
from agentmesh.inverse import inverse_linear,cross_coupling,reflexive_feedback

matrix=[[1.0,0.25],[0.2,1.0]]
target=[2.0,1.0]
inverse=inverse_linear(matrix,target,ridge=0.001)
crossed=cross_coupling(matrix,inverse)
feedback=reflexive_feedback(matrix,[0.0,0.0],target,gain=0.4,max_steps=100)
print(json.dumps({"inverse":inverse,"crossed":crossed,
                  "feedback":{"converged":feedback.converged,
                              "state":feedback.state,
                              "iterations":feedback.iterations,
                              "residual":feedback.residual,
                              "history":feedback.history}},indent=2))
