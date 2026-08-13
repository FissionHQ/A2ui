from app.config import Settings, get_settings
from app.llm.gemini_provider import GeminiProvider
from app.llm.stubs import (
    AnthropicProvider,
    AzureOpenAIProvider,
    OllamaProvider,
    OpenAICompatibleProvider,
    OpenAIProvider,
)


def create_llm(settings: Settings | None = None):
    settings = settings or get_settings()
    provider = settings.llm_provider.lower().strip()
    if not settings.llm_configured:
        return None
    if provider in {"gemini", "google", "google-gemini"}:
        return GeminiProvider(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            generation_model=settings.gemini_generation_model,
            base_url=settings.llm_base_url,
        )
    if provider == "openai":
        return OpenAIProvider()
    if provider == "anthropic":
        return AnthropicProvider()
    if provider == "ollama":
        return OllamaProvider()
    if provider in {"azure", "azure-openai"}:
        return AzureOpenAIProvider()
    return OpenAICompatibleProvider()
