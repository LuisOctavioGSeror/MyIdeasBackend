from openai import OpenAI
from app.core.config import get_settings
from app.infrastructure.llm.openai_client import OpenAIClient

class GroqClient(OpenAIClient):
    """
    Usa o endpoint OpenAI-compatível da Groq.
    Mantém o mesmo mapeamento de tools e o loop de tool-calling.
    """
    def __init__(self, model: str | None = None):
        s = get_settings()
        # IMPORTANTe: base_url aponta para Groq
        self.client = OpenAI(
            api_key=s.groq_api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        # Não force default aqui: prefira exigir GROQ_MODEL via env
        if not (model or s.groq_model):
            # evita surpresa silenciosa; fale claro se não tiver modelo
            raise ValueError("GROQ_MODEL não definido. Configure a env GROQ_MODEL.")
        self.model = model or s.groq_model
