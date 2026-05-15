from pathlib import Path

from playwright.sync_api import Page


def capture_failure_artifacts(page: Page, artifacts_dir: Path, test_name: str) -> None:
    """Save screenshot and DOM source for a failed test."""

    safe_name = test_name.replace("/", "_").replace("\\", "_").replace("::", "__")
    output_dir = artifacts_dir / "failures" / safe_name
    output_dir.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(output_dir / "screenshot.png"), full_page=True)
    (output_dir / "dom.html").write_text(page.content(), encoding="utf-8")
