"""Conservative deployment safety configuration for AgentMesh."""
from dataclasses import dataclass
from ipaddress import ip_address
import os

def loopback(host: str)->bool:
    if host=="localhost":return True
    try:return ip_address(host).is_loopback
    except ValueError:return False

@dataclass(frozen=True)
class DeploymentConfig:
    host: str
    token: str
    db_path: str
    allow_remote: bool = False

    @classmethod
    def from_env(cls,host):
        return cls(host,os.getenv("AGENTMESH_API_TOKEN",""),
                   os.getenv("AGENTMESH_DB_PATH",""),
                   os.getenv("AGENTMESH_ALLOW_REMOTE","")=="1")

    def validate(self):
        if not loopback(self.host):
            if not self.allow_remote:
                raise ValueError("Non-loopback host requires AGENTMESH_ALLOW_REMOTE=1")
            if len(self.token)<32:
                raise ValueError("Remote binding requires a bearer token of at least 32 characters")
        if self.token and len(self.token)<16:
            raise ValueError("Bearer token must have at least 16 characters")
        return True
