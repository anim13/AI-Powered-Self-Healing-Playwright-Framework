from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class HealingSuggestion:
    """One possible replacement locator returned by an AI or rule-based model."""

    strategy: str
    value: str
    confidence: float
    reason: str


class AIProvider(Protocol):
    """Contract for any model that can suggest locator replacements."""

    def suggest_locators(
        self,
        *,
        failed_strategy: str,
        failed_value: str,
        element_name: str,
        dom_snapshot: str,
    ) -> list[HealingSuggestion]:
        """Return ranked replacement locators for a failed element."""


class RulesBasedAIProvider:
    """Deterministic provider used for local demos, CI, and offline execution."""

    def suggest_locators(
        self,
        *,
        failed_strategy: str,
        failed_value: str,
        element_name: str,
        dom_snapshot: str,
    ) -> list[HealingSuggestion]:
        """Infer accessible and stable locator candidates from known element intent."""

        normalized_name = element_name.strip().replace("_", " ").title()
        raw_name = element_name.strip().replace("_", "-").lower()
        candidates = [
            HealingSuggestion(
                strategy="role",
                value=f"button::{normalized_name}",
                confidence=0.91,
                reason="Accessible role and name are usually resilient across CSS changes.",
            ),
            HealingSuggestion(
                strategy="test_id",
                value=raw_name,
                confidence=0.84,
                reason="data-testid is a stable automation contract when available.",
            ),
            HealingSuggestion(
                strategy="text",
                value=normalized_name,
                confidence=0.72,
                reason="Visible text is a useful fallback for user-facing controls.",
            ),
        ]
        return candidates
