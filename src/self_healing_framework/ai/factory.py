from self_healing_framework.ai.openai_provider import OpenAIProvider
from self_healing_framework.ai.provider import AIProvider, RulesBasedAIProvider
from self_healing_framework.config import Settings


def build_ai_provider(settings: Settings) -> AIProvider:
    """Create the configured AI provider."""

    if settings.ai_provider.lower() == "openai":
        return OpenAIProvider(settings)
    return RulesBasedAIProvider()
