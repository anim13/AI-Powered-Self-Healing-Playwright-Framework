from playwright.sync_api import Error, Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from self_healing_framework.ai.provider import AIProvider
from self_healing_framework.healing.locator import LocatorDefinition, from_suggestion
from self_healing_framework.healing.store import HealingStore


class HealingEngine:
    """Attempts to recover failed locators using model-suggested alternatives."""

    def __init__(
        self,
        *,
        page: Page,
        ai_provider: AIProvider,
        store: HealingStore,
        enabled: bool = True,
    ) -> None:
        self.page = page
        self.ai_provider = ai_provider
        self.store = store
        self.enabled = enabled

    def locate(self, locator: LocatorDefinition) -> Locator:
        """Return the original locator or a validated healed replacement."""

        original = locator.resolve(self.page)
        if not self.enabled:
            return original

        if self._is_usable(original):
            return original

        dom_snapshot = self.capture_dom_snapshot()
        suggestions = self.ai_provider.suggest_locators(
            failed_strategy=locator.strategy,
            failed_value=locator.value,
            element_name=locator.name,
            dom_snapshot=dom_snapshot,
        )
        for suggestion in sorted(suggestions, key=lambda item: item.confidence, reverse=True):
            candidate_definition = from_suggestion(
                name=locator.name,
                strategy=suggestion.strategy,
                value=suggestion.value,
            )
            candidate = candidate_definition.resolve(self.page)
            if self._is_usable(candidate):
                self.store.append(
                    element_name=locator.name,
                    failed_strategy=locator.strategy,
                    failed_value=locator.value,
                    healed_strategy=suggestion.strategy,
                    healed_value=suggestion.value,
                    confidence=suggestion.confidence,
                    reason=suggestion.reason,
                )
                return candidate

        return original

    def capture_dom_snapshot(self) -> str:
        """Capture the current DOM as compact text for AI analysis."""

        return self.page.locator("body").evaluate("body => body.outerHTML")

    def _is_usable(self, locator: Locator) -> bool:
        """Check whether a locator resolves to exactly one visible element."""

        try:
            return locator.count() == 1 and locator.first.is_visible(timeout=750)
        except (Error, PlaywrightTimeoutError):
            return False
