from playwright.sync_api import Locator, Page, expect

from self_healing_framework.healing.engine import HealingEngine
from self_healing_framework.healing.locator import LocatorDefinition


class BasePage:
    """Base class for all page objects."""

    def __init__(self, page: Page, healing_engine: HealingEngine) -> None:
        self.page = page
        self.healing_engine = healing_engine

    def open(self, path: str = "/") -> None:
        """Navigate to a path relative to BASE_URL."""

        self.page.goto(path)

    def element(self, locator: LocatorDefinition) -> Locator:
        """Resolve an element through the self-healing locator engine."""

        return self.healing_engine.locate(locator)

    def click(self, locator: LocatorDefinition) -> None:
        """Click an element after healing has had a chance to resolve it."""

        self.element(locator).click()

    def fill(self, locator: LocatorDefinition, value: str) -> None:
        """Fill an input after resolving it through the healing engine."""

        self.element(locator).fill(value)

    def text_of(self, locator: LocatorDefinition) -> str:
        """Return visible text for an element."""

        return self.element(locator).inner_text()

    def should_be_visible(self, locator: LocatorDefinition) -> None:
        """Assert that an element is visible."""

        expect(self.element(locator)).to_be_visible()
