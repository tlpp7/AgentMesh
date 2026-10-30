"""Optional OpenAI Responses API gateway with bounded, testable requests."""
from dataclasses import dataclass
from time import perf_counter
import os

@dataclass(frozen=True)
class ModelConfig:
    model: str
    max_output_tokens: int = 512
    timeout_seconds: float = 20.0
    def __post_init__(self):
        if not isinstance(self.model,str) or not self.model.strip() or len(self.model)>100:
            raise ValueError("model must be a nonempty identifier")
        if type(self.max_output_tokens) is not int or not 1<=self.max_output_tokens<=4096:
            raise ValueError("max_output_tokens out of bounds")
        if not 1<=self.timeout_seconds<=60:
            raise ValueError("timeout outside 1..60 seconds")

class ModelGateway:
    """Client is injected for offline tests; no secret is ever returned or logged."""
    def __init__(self, config: ModelConfig, client=None):
        self.config=config
        if client is None:
            if not os.getenv("OPENAI_API_KEY"):
                raise RuntimeError("OPENAI_API_KEY is not configured")
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise RuntimeError("Install optional dependency: pip install -e '.[openai]'") from exc
            client=OpenAI(api_key=os.environ["OPENAI_API_KEY"],timeout=config.timeout_seconds,max_retries=0)
        self.client=client

    def generate(self, objective: str, instructions: str) -> dict:
        if not isinstance(objective,str) or not 1<=len(objective.strip())<=5000:
            raise ValueError("objective must contain 1..5000 characters")
        if not isinstance(instructions,str) or not 1<=len(instructions.strip())<=2000:
            raise ValueError("instructions must contain 1..2000 characters")
        started=perf_counter()
        try:
            response=self.client.responses.create(
                model=self.config.model,
                instructions=instructions,
                input=objective,
                max_output_tokens=self.config.max_output_tokens,
                store=False)
        except Exception as exc:
            # Avoid leaking upstream request headers/credentials/prompt in errors.
            raise RuntimeError("model_provider_request_failed") from None
        output=getattr(response,"output_text",None)
        if not isinstance(output,str) or not output.strip():
            raise RuntimeError("model_provider_empty_output")
        usage=getattr(response,"usage",None)
        return {"output":output,"model":self.config.model,
                "duration_ms":round((perf_counter()-started)*1000,3),
                "usage":{"input_tokens":getattr(usage,"input_tokens",None),
                         "output_tokens":getattr(usage,"output_tokens",None)}}
