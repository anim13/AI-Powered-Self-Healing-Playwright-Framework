import pytest

from self_healing_framework.healing.store import HealingStore
from tests.pages.login_page import LoginPage


@pytest.mark.e2e
@pytest.mark.healing
def test_login_button_locator_self_heals(page, healing_engine, settings):
    """Proves that a stale CSS locator can recover through accessible role fallback."""

    login_page = LoginPage(page, healing_engine)
    login_page.load_demo_markup()

    login_page.login(username="anina", password="secret")

    login_page.should_show_welcome_message("anina")
    records = HealingStore(settings.reports_dir / "healing-events.jsonl").read_all()
    assert any(
        record.element_name == "login"
        and record.failed_strategy == "css"
        and record.healed_strategy in {"role", "test_id", "text"}
        for record in records
    )
