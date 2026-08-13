from app.llm.base import LLMError


class _Unconfigured:
    def __init__(self, name: str):
        self.name = name
        self.model = ""

    async def complete_json(self, *, system: str, user: str, schema: dict | None = None):
        raise LLMError(f"{self.name} provider is not selected for this demo")

    async def complete_text_stream(self, *, system: str, user: str):
        raise LLMError(f"{self.name} provider is not selected for this demo")
        yield  # pragma: no cover


class OpenAIProvider(_Unconfigured):
    def __init__(self, *args, **kwargs):
        super().__init__("openai")


class AnthropicProvider(_Unconfigured):
    def __init__(self, *args, **kwargs):
        super().__init__("anthropic")


class OllamaProvider(_Unconfigured):
    def __init__(self, *args, **kwargs):
        super().__init__("ollama")


class OpenAICompatibleProvider(_Unconfigured):
    def __init__(self, *args, **kwargs):
        super().__init__("openai-compatible")


class AzureOpenAIProvider(_Unconfigured):
    def __init__(self, *args, **kwargs):
        super().__init__("azure-openai")
