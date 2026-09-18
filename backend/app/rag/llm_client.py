"""
HTTP client for a local Ollama instance running Llama 3.
"""
import httpx

from app.config import settings


class OllamaUnavailableError(Exception):
    """Raised when Ollama cannot be reached, so callers can return a 503."""


class OllamaClient:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL

    async def generate(self, prompt: str, system: str = None, temperature: float = 0.3) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(f"{self.base_url}/api/generate", json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("response", "").strip()
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            raise OllamaUnavailableError(f"Ollama est injoignable à l'adresse {self.base_url}") from e
        except httpx.HTTPStatusError as e:
            raise OllamaUnavailableError(f"Erreur Ollama : {e}") from e

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False


_client: OllamaClient = None


def get_llm_client() -> OllamaClient:
    global _client
    if _client is None:
        _client = OllamaClient()
    return _client
