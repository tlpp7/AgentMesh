from agentmesh import Constraint, Mesh, Task

result = Mesh().run(
    Task("Build a safe pipeline", [Constraint("review", lambda output: "Review:" in output)])
)
print(result.to_dict())
