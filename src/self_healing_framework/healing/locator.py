from dataclasses import dataclass

from playwright.sync_api import Locator, Page


@dataclass(frozen=True)
class LocatorDefinition:
    """Serializable locator contract used by page objects and the healing engine."""

    strategy: str
    value: str
    name: str

    def resolve(self, page: Page) -> Locator:
        """Convert this locator definition into a Playwright Locator."""

        if self.strategy == "css":
            return page.locator(self.value)
        if self.strategy == "xpath":
            return page.locator(f"xpath={self.value}")
        if self.strategy == "text":
            return page.get_by_text(self.value)
        if self.strategy == "test_id":
            return page.get_by_test_id(self.value)
        if self.strategy == "role":
            role, accessible_name = self.value.split("::", maxsplit=1)
            return page.get_by_role(role, name=accessible_name)
        raise ValueError(f"Unsupported locator strategy: {self.strategy}")


def from_suggestion(name: str, strategy: str, value: str) -> LocatorDefinition:
    """Build a locator definition from a healing suggestion."""

    return LocatorDefinition(strategy=strategy, value=value, name=name)
