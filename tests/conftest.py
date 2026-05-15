import pytest
from playwright.sync_api import Browser, Page, Playwright, sync_playwright

from self_healing_framework.ai.factory import build_ai_provider
from self_healing_framework.browser import BrowserFactory, page_session
from self_healing_framework.config import Settings, get_settings
from self_healing_framework.healing.engine import HealingEngine
from self_healing_framework.healing.store import HealingStore
from self_healing_framework.reporting import capture_failure_artifacts


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Expose framework settings to tests and fixtures."""

    return get_settings()


@pytest.fixture(scope="session")
def playwright_instance() -> Playwright:
    """Start Playwright once per test session."""

    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright, settings: Settings) -> Browser:
    """Launch one browser per test session."""

    browser_factory = BrowserFactory(playwright_instance, settings)
    browser = browser_factory.launch_browser()
    yield browser
    browser.close()


@pytest.fixture()
def page(browser: Browser, settings: Settings) -> Page:
    """Create an isolated page per test."""

    yield from page_session(browser, settings)


@pytest.fixture()
def healing_engine(page: Page, settings: Settings) -> HealingEngine:
    """Create the self-healing engine used by page objects."""

    store = HealingStore(settings.reports_dir / "healing-events.jsonl")
    return HealingEngine(
        page=page,
        ai_provider=build_ai_provider(settings),
        store=store,
        enabled=settings.self_healing_enabled,
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[object]):
    """Capture artifacts when a test call fails and the page fixture exists."""

    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed and "page" in item.funcargs:
        settings = get_settings()
        capture_failure_artifacts(item.funcargs["page"], settings.artifacts_dir, item.nodeid)
