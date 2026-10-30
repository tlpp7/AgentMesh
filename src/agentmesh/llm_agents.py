"""Configurable LLM role pipeline built on the existing bounded Mesh."""
from dataclasses import dataclass
from .core import Agent, Mesh, Task, Constraint

@dataclass(frozen=True)
class AgentRole:
    name: str
    instructions: str
    def __post_init__(self):
        if not self.name.strip() or not 1<=len(self.instructions.strip())<=2000:
            raise ValueError("invalid agent role")

DEFAULT_ROLES=(
    AgentRole("analyzer","Analyze the task, assumptions and possible failure modes. Do not invent facts."),
    AgentRole("proposer","Provide a concrete plan with verifiable acceptance criteria."),
    AgentRole("critic","Review the proposal for weaknesses and missing evidence."),
)

def run_llm_pipeline(objective: str, gateway, roles=DEFAULT_ROLES, max_attempts=1):
    """No automatic re-execution by default, because real LLM calls cost money."""
    if not 1<=len(roles)<=8 or len(set(r.name for r in roles))!=len(roles):
        raise ValueError("roles must have unique names (1..8)")
    if not 1<=max_attempts<=3:
        raise ValueError("max_attempts must be 1..3")
    def build(role):
        def execute(text,task):
            answer=gateway.generate(text,role.instructions)
            return answer["output"]
        return Agent(role.name,execute)
    result=Mesh([build(r) for r in roles],max_attempts=max_attempts).run(
        Task(objective,[Constraint("nonempty",lambda text:bool(text.strip()))]))
    return result.to_dict()
