import json

from self_healing_framework.ai.provider import HealingSuggestion
from self_healing_framework.config import Settings


class OpenAIProvider:
    """OpenAI-backed locator suggestion provider.

    This class is optional. The framework can run fully offline with RulesBasedAIProvider.
    """

    def __init__(self, settings: Settings) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when AI_PROVIDER=openai")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("Install optional dependencies with: pip install -e .[ai]") from exc

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def suggest_locators(
        self,
        *,
        failed_strategy: str,
        failed_value: str,
        element_name: str,
        dom_snapshot: str,
    ) -> list[HealingSuggestion]:
        """Ask the model to produce ranked locator candidates as strict JSON."""

        prompt = {
            "task": "Suggest resilient Playwright locators for a failed UI element.",
            "failed_locator": {"strategy": failed_strategy, "value": failed_value},
            "element_name": element_name,
            "dom_snapshot": dom_snapshot[:12000],
            "allowed_strategies": ["role", "test_id", "text", "css", "xpath"],
            "response_schema": [
                {"strategy": "role", "value": "button::Save", "confidence": 0.9, "reason": "..."}
            ],
        }
        response = self.client.responses.create(
            model=self.model,
            input=f"Return only JSON. Payload: {json.dumps(prompt)}",
        )
        raw_text = response.output_text
        parsed = json.loads(raw_text)
        return [
            HealingSuggestion(
                strategy=item["strategy"],
                value=item["value"],
                confidence=float(item["confidence"]),
                reason=item["reason"],
            )
            for item in parsed
        ]
