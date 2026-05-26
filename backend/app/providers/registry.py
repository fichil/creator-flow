from app.providers.fake_llm import FakeLLMProvider
from app.providers.llm import LLMProvider

_LLM_PROVIDERS: dict[str, LLMProvider] = {
    FakeLLMProvider.provider_name: FakeLLMProvider(),
}


def get_llm_provider(name: str = "fake_llm") -> LLMProvider:
    return _LLM_PROVIDERS[name]
