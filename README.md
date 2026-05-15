# AI-Powered Self-Healing Playwright Framework

Portfolio-level automation framework using **Python + Pytest + Playwright** with an AI-assisted locator recovery layer.

The goal is to demonstrate architecture thinking, maintainability, CI/CD readiness, and a realistic solution to a common industry problem: brittle UI tests caused by locator drift.

## What This Framework Solves

Modern web apps change frequently. CSS classes, IDs, DOM nesting, and labels can shift even when the user workflow still works. Traditional automation fails immediately when a locator is stale.

This framework:

- Tries the original locator first.
- Captures DOM context when the locator is not usable.
- Sends the failed locator and DOM context to an AI provider.
- Receives ranked locator candidates.
- Validates each candidate in the real browser.
- Uses the first working locator.
- Stores a healing audit record for review.

## Architecture

```text
Pytest Test
   |
   v
Page Object
   |
   v
BasePage.element()
   |
   v
HealingEngine.locate()
   |
   +--> Original locator works --> use it
   |
   +--> Original locator fails
          |
          v
       Capture DOM
          |
          v
       AIProvider.suggest_locators()
          |
          v
       Validate candidates in Playwright
          |
          v
       Save healing event + continue test
```

## Project Structure

```text
.
├── .github/workflows/tests.yml
├── .env.example
├── pyproject.toml
├── pytest.ini
├── README.md
├── src/self_healing_framework/
│   ├── ai/
│   ├── browser.py
│   ├── config.py
│   ├── healing/
│   ├── pages/
│   └── reporting/
└── tests/
    ├── conftest.py
    ├── e2e/
    ├── pages/
    └── unit/
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .[dev]
python -m playwright install chromium
```

Run tests:

```powershell
pytest
```

Run with HTML report:

```powershell
pytest --html=reports/pytest-report.html --self-contained-html
```

## Configuration

Copy `.env.example` to `.env` and update values as needed.

| Variable | Purpose |
| --- | --- |
| `BASE_URL` | Base URL for real application tests. |
| `BROWSER` | Browser engine: `chromium`, `firefox`, or `webkit`. |
| `HEADLESS` | Runs browser headless when `true`. |
| `SLOW_MO` | Adds Playwright slow motion in milliseconds. |
| `DEFAULT_TIMEOUT_MS` | Default timeout for page actions. |
| `SELF_HEALING_ENABLED` | Turns healing on or off. |
| `AI_PROVIDER` | `rules` for deterministic local provider, `openai` for OpenAI provider. |
| `OPENAI_API_KEY` | Required only when `AI_PROVIDER=openai`. |
| `OPENAI_MODEL` | Model used by the OpenAI provider. |

## File And Method Explanation

### `src/self_healing_framework/config.py`

`Settings`
: Central Pydantic settings class. Reads environment variables such as browser, base URL, timeout, AI provider, and report paths.

`get_settings()`
: Cached settings factory. Prevents different fixtures from loading conflicting config values.

### `src/self_healing_framework/browser.py`

`BrowserFactory.__init__(playwright, settings)`
: Stores Playwright and framework settings.

`BrowserFactory.launch_browser()`
: Launches the configured browser engine using `BROWSER`, `HEADLESS`, and `SLOW_MO`.

`BrowserFactory.new_context(browser)`
: Creates an isolated browser context with base URL, viewport, and video recording.

`page_session(browser, settings)`
: Creates a page for one test, starts tracing, yields the page, saves trace output, and closes the context.

### `src/self_healing_framework/healing/locator.py`

`LocatorDefinition`
: Serializable locator object used by page classes. It stores `strategy`, `value`, and logical `name`.

`LocatorDefinition.resolve(page)`
: Converts a framework locator into a Playwright `Locator`. Supported strategies are `css`, `xpath`, `text`, `test_id`, and `role`.

`from_suggestion(name, strategy, value)`
: Converts an AI suggestion into a `LocatorDefinition`.

### `src/self_healing_framework/healing/engine.py`

`HealingEngine.__init__(page, ai_provider, store, enabled)`
: Wires the browser page, AI provider, healing event store, and feature flag.

`HealingEngine.locate(locator)`
: Main self-healing method. It checks the original locator, captures DOM if needed, asks AI for alternatives, validates candidates, records successful healing, and returns a working Playwright locator.

`HealingEngine.capture_dom_snapshot()`
: Returns the current page body HTML so the AI provider has context.

`HealingEngine._is_usable(locator)`
: Returns `True` only when a locator resolves to exactly one visible element. This prevents healing to ambiguous or hidden elements.

### `src/self_healing_framework/healing/store.py`

`HealingRecord`
: Dataclass representing one healing event.

`HealingStore.__init__(path)`
: Creates a JSON Lines store at the provided path.

`HealingStore.append(...)`
: Persists a successful healing decision with failed locator, healed locator, confidence, reason, and timestamp.

`HealingStore.read_all()`
: Reads all saved healing records for tests, reports, or dashboards.

### `src/self_healing_framework/ai/provider.py`

`HealingSuggestion`
: Dataclass representing a ranked locator candidate.

`AIProvider`
: Protocol that defines the expected interface for any AI provider.

`RulesBasedAIProvider.suggest_locators(...)`
: Offline deterministic provider that mimics AI behavior by generating stable locator candidates from element intent. This is useful for CI and demos.

### `src/self_healing_framework/ai/openai_provider.py`

`OpenAIProvider.__init__(settings)`
: Validates OpenAI configuration and creates the OpenAI client.

`OpenAIProvider.suggest_locators(...)`
: Sends failed locator data and DOM snapshot to the model, expects strict JSON, and converts the response into `HealingSuggestion` objects.

### `src/self_healing_framework/ai/factory.py`

`build_ai_provider(settings)`
: Returns either `RulesBasedAIProvider` or `OpenAIProvider` based on `AI_PROVIDER`.

### `src/self_healing_framework/pages/base_page.py`

`BasePage.__init__(page, healing_engine)`
: Stores the Playwright page and healing engine for child page objects.

`BasePage.open(path)`
: Navigates to a path relative to `BASE_URL`.

`BasePage.element(locator)`
: Resolves a locator through the self-healing engine.

`BasePage.click(locator)`
: Clicks a healed or original element.

`BasePage.fill(locator, value)`
: Fills a healed or original input.

`BasePage.text_of(locator)`
: Returns text from a healed or original element.

`BasePage.should_be_visible(locator)`
: Asserts visibility using Playwright assertions.

### `src/self_healing_framework/reporting/artifacts.py`

`capture_failure_artifacts(page, artifacts_dir, test_name)`
: Saves screenshot and DOM HTML when a test fails.

### `tests/conftest.py`

`settings()`
: Provides global framework settings to tests.

`playwright_instance()`
: Starts Playwright once per test session.

`browser()`
: Launches the configured browser once per session.

`page()`
: Creates an isolated page per test using tracing and video configuration.

`healing_engine()`
: Builds the healing engine with configured AI provider and healing store.

`pytest_runtest_makereport(...)`
: Pytest hook that captures screenshots and DOM for failed tests.

### `tests/pages/login_page.py`

`LoginPage`
: Demo page object. It intentionally defines `login_button` with stale CSS `#login-btn-old` while the actual button uses `#login-btn-new`.

`load_demo_markup()`
: Loads a small in-memory HTML app for reliable local testing.

`login(username, password)`
: Fills username, fills password, and clicks the login button through the self-healing engine.

`should_show_welcome_message(username)`
: Verifies the login flow succeeded.

### `tests/e2e/test_login_self_healing.py`

`test_login_button_locator_self_heals(...)`
: End-to-end proof that the stale CSS locator heals to a valid role, test ID, or text locator and records the event.

### `tests/unit/test_rules_based_provider.py`

`test_rules_based_provider_returns_ranked_locator_suggestions()`
: Unit test proving the deterministic provider returns ranked suggestions.

### `.github/workflows/tests.yml`

GitHub Actions pipeline that installs Python dependencies, installs Playwright Chromium, runs tests, and uploads reports/artifacts.

## GenAI Integration Strategy

The project uses an `AIProvider` interface so the framework is not tightly coupled to one vendor.

For local and CI execution:

```env
AI_PROVIDER=rules
```

For real GenAI integration:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4.1-mini
```

The OpenAI provider receives:

- Failed locator strategy and value.
- Logical element name from the page object.
- Current DOM snapshot.
- Allowed locator strategies.

It returns ranked locator candidates. The framework does not blindly trust the model. Every suggestion is validated in Playwright before use.

## Scalability And CI/CD Considerations

- Browser is session-scoped; page/context is test-scoped for isolation.
- Healing events are saved as JSON Lines for easy ingestion into dashboards.
- Screenshots, DOM, videos, and traces are generated for debugging.
- AI provider is swappable, allowing OpenAI, Azure OpenAI, local LLMs, or rules-based execution.
- Healing can be disabled with `SELF_HEALING_ENABLED=false` for strict validation gates.
- CI uploads reports and artifacts for debugging failed builds.

## Resume Impact Statement

Designed and implemented an AI-powered self-healing Playwright automation framework using Python and Pytest, with DOM-aware locator recovery, pluggable GenAI provider architecture, traceable healing audit logs, failure artifact capture, and GitHub Actions CI/CD integration.
