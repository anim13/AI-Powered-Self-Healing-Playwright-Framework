from playwright.sync_api import expect

from self_healing_framework.healing.locator import LocatorDefinition
from self_healing_framework.pages import BasePage


class LoginPage(BasePage):
    """Demo page object with one intentionally stale locator."""

    username_input = LocatorDefinition(strategy="test_id", value="username", name="username")
    password_input = LocatorDefinition(strategy="test_id", value="password", name="password")
    login_button = LocatorDefinition(strategy="css", value="#login-btn-old", name="login")
    welcome_message = LocatorDefinition(
        strategy="test_id",
        value="welcome-message",
        name="welcome_message",
    )

    def load_demo_markup(self) -> None:
        """Load a small in-memory application used by portfolio tests."""

        self.page.set_content(
            """
            <main>
              <h1>Banking Portal</h1>
              <label>Username <input data-testid="username" /></label>
              <label>Password <input data-testid="password" type="password" /></label>
              <button id="login-btn-new" data-testid="login" onclick="
                document.querySelector('[data-testid=welcome-message]').textContent =
                  'Welcome, ' + document.querySelector('[data-testid=username]').value;
              ">Login</button>
              <p data-testid="welcome-message"></p>
            </main>
            """
        )

    def login(self, username: str, password: str) -> None:
        """Complete the login workflow."""

        self.fill(self.username_input, username)
        self.fill(self.password_input, password)
        self.click(self.login_button)

    def should_show_welcome_message(self, username: str) -> None:
        """Verify that login succeeded."""

        expect(self.element(self.welcome_message)).to_have_text(f"Welcome, {username}")
