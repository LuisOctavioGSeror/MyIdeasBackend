from app.core.config import get_settings
from app.infrastructure.llm.openai_client import OpenAIClient
from app.infrastructure.llm.anthropic_client import AnthropicClient
from app.infrastructure.llm.groq_client import GroqClient  # <- novo

def get_llm_client(provider: str | None, model: str | None):
    s = get_settings()
    prov = (provider or s.llm_provider).lower()
    if prov == "openai":
        if not s.openai_api_key:
            raise ValueError(
                "Missing OPENAI_API_KEY. Set it in your environment or .env (LLM_PROVIDER=openai)."
            )
        return OpenAIClient(model=model or s.openai_model)
    if prov == "anthropic":
        if not s.anthropic_api_key:
            raise ValueError(
                "Missing ANTHROPIC_API_KEY. Set it in your environment or .env (LLM_PROVIDER=anthropic)."
            )
        return AnthropicClient(model=model or s.anthropic_model)
    if prov == "groq":
        if not s.groq_api_key:
            raise ValueError(
                "Missing GROQ_API_KEY. Set it in your environment or .env (LLM_PROVIDER=groq)."
            )
        return GroqClient(model=model or s.groq_model)
    raise ValueError(f"Unsupported provider: {prov}")
