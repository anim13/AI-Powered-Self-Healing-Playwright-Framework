from collections.abc import Iterator

from playwright.sync_api import Browser, BrowserContext, Page, Playwright

from self_healing_framework.config import Settings


class BrowserFactory:
    """Creates Playwright browsers and contexts from framework settings."""

    def __init__(self, playwright: Playwright, settings: Settings) -> None:
        self.playwright = playwright
        self.settings = settings

    def launch_browser(self) -> Browser:
        """Launch the configured browser type."""

        browser_launcher = getattr(self.playwright, self.settings.browser)
        return browser_launcher.launch(
            headless=self.settings.headless,
            slow_mo=self.settings.slow_mo,
        )

    def new_context(self, browser: Browser) -> BrowserContext:
        """Create an isolated browser context for one test."""

        return browser.new_context(
            base_url=self.settings.base_url,
            viewport={"width": 1440, "height": 900},
            record_video_dir=str(self.settings.artifacts_dir / "videos"),
        )


def page_session(browser: Browser, settings: Settings) -> Iterator[Page]:
    """Yield a page with tracing enabled, then close the context cleanly."""

    context = browser.new_context(
        base_url=settings.base_url,
        viewport={"width": 1440, "height": 900},
        record_video_dir=str(settings.artifacts_dir / "videos"),
    )
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page = context.new_page()
    page.set_default_timeout(settings.default_timeout_ms)
    try:
        yield page
    finally:
        trace_path = settings.artifacts_dir / "traces" / "trace.zip"
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        context.tracing.stop(path=str(trace_path))
        context.close()
