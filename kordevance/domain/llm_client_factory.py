from kordevance.domain.models.llm_provider import AuthorizedLLMProviders, LLMProvider

DEFAULT_PROVIDER_ENDPOINTS: dict[AuthorizedLLMProviders, str] = {
    AuthorizedLLMProviders.DeepSeek: "https://api.deepseek.com",
    AuthorizedLLMProviders.Anthropic: "https://api.anthropic.com",
    AuthorizedLLMProviders.OpenRouter: "https://openrouter.ai/api/v1",
    AuthorizedLLMProviders.OpenAI: "https://api.openai.com/v1",
    AuthorizedLLMProviders.Gemini: "https://generativelanguage.googleapis.com",
    AuthorizedLLMProviders.Mistral: "https://api.mistral.ai",
    AuthorizedLLMProviders.XAI: "https://api.x.ai",
}


class LLMProviderFactory:
    @staticmethod
    def parse_provider(provider: str) -> AuthorizedLLMProviders | None:
        try:
            return AuthorizedLLMProviders(provider)
        except ValueError:
            return None

    @staticmethod
    def _get_default_endpoint(provider: AuthorizedLLMProviders) -> str:
        try:
            return DEFAULT_PROVIDER_ENDPOINTS[provider]
        except KeyError as err:
            raise ValueError(f"No default endpoint configured for provider: {provider}") from err

    @classmethod
    def build_client(
        cls,
        provider: AuthorizedLLMProviders,
        endpoint: str | None,
        api_key: str,
        display_name: str | None = None,
    ) -> LLMProvider:
        if provider == AuthorizedLLMProviders.Other:
            if not endpoint:
                raise ValueError("An endpoint is required for provider type 'other'")
            if not display_name:
                raise ValueError("A display name is required for provider type 'other'")
        else:
            endpoint = endpoint or cls._get_default_endpoint(provider)

        return LLMProvider(name=provider, endpoint=endpoint, api_key=api_key, display_name=display_name)
