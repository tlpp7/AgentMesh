import pytest
from types import SimpleNamespace
from agentmesh.model_gateway import ModelConfig,ModelGateway
from agentmesh.llm_agents import run_llm_pipeline,AgentRole

class FakeResponses:
    def __init__(self):self.calls=[]
    def create(self,**kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text="Verified output",usage=SimpleNamespace(input_tokens=10,output_tokens=5))
class FakeClient:
    def __init__(self):self.responses=FakeResponses()

def test_offline_gateway():
    fake=FakeClient()
    gateway=ModelGateway(ModelConfig("test-model",100,5),client=fake)
    result=gateway.generate("Test objective","Follow constraints")
    assert result["output"]=="Verified output"
    assert result["usage"]["input_tokens"]==10
    assert fake.responses.calls[0]["store"] is False
    assert fake.responses.calls[0]["max_output_tokens"]==100

def test_config_rejects_budget():
    with pytest.raises(ValueError):ModelConfig("test",0)
    with pytest.raises(ValueError):ModelConfig("test",512,100)

def test_key_is_required_without_fake(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY",raising=False)
    with pytest.raises(RuntimeError,match="OPENAI_API_KEY"):
        ModelGateway(ModelConfig("test"))

def test_pipeline_roles():
    fake=FakeClient()
    result=run_llm_pipeline("Describe a system",ModelGateway(ModelConfig("test"),fake),
        roles=(AgentRole("analyzer","Analyze carefully"),AgentRole("critic","Verify claims")))
    assert result["accepted"]
    assert result["metrics"]["agent_calls"]==2
    assert len(fake.responses.calls)==2

def test_provider_errors_are_sanitized():
    class Broken:
        class responses:
            @staticmethod
            def create(**kwargs):raise Exception("secret-token-leak")
    gateway=ModelGateway(ModelConfig("test"),Broken())
    with pytest.raises(RuntimeError) as exc:
        gateway.generate("objective","instructions")
    assert "secret-token-leak" not in str(exc.value)
