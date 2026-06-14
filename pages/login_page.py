"""
login_page.py — Page Object for the Login page.

Encapsulates all locators and user-facing actions related to
authentication. Tests never touch Playwright selectors directly.
"""

import logging

from playwright.sync_api import Page, Locator

from pages.base_page import BasePage
from utils.config import config

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """
    Page Object Model for the application login screen.

    Target: https://practicetestautomation.com/practice-test-login/

    Locators are defined as properties so they are lazily evaluated
    and always return a fresh Locator bound to the current page.
    """

    # ── URL ───────────────────────────────────────────────────────────────────

    URL: str = config.base_url

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ── Locators (properties) ─────────────────────────────────────────────────

    @property
    def username_input(self) -> Locator:
        """Text input for the username / email."""
        return self.page.locator("#username")

    @property
    def password_input(self) -> Locator:
        """Text input for the password."""
        return self.page.locator("#password")

    @property
    def submit_button(self) -> Locator:
        """The 'Log In' / Submit button."""
        return self.page.locator("#submit")

    @property
    def error_message(self) -> Locator:
        """Inline error banner shown on failed login attempts."""
        return self.page.locator("#error")

    @property
    def success_heading(self) -> Locator:
        """Heading displayed after a successful login ('Logged In Successfully')."""
        return self.page.locator("h1")

    @property
    def logout_button(self) -> Locator:
        """'Log out' link available on the post-login page."""
        return self.page.locator(".wp-block-button a")

    # ── Actions ───────────────────────────────────────────────────────────────

    def open(self) -> "LoginPage":
        """Navigate to the login page and return self for chaining."""
        logger.info(f"Opening login page: {self.URL}")
        self.navigate(self.URL)
        return self

    def enter_username(self, username: str) -> "LoginPage":
        """Type *username* into the username field."""
        logger.debug(f"Entering username: {username!r}")
        self.username_input.fill(username)
        return self

    def enter_password(self, password: str) -> "LoginPage":
        """Type *password* into the password field (value not logged)."""
        logger.debug("Entering password: [MASKED]")
        self.password_input.fill(password)
        return self

    def click_submit(self) -> "LoginPage":
        """Click the submit button and return self."""
        logger.debug("Clicking submit button")
        self.submit_button.click()
        return self

    def login(self, username: str, password: str) -> "LoginPage":
        """
        High-level helper: fill credentials and submit the form.

        Args:
            username: The account username or email.
            password: The account password.

        Returns:
            Self, allowing method chaining.
        """
        logger.info(f"Attempting login with username: {username!r}")
        return (
            self.enter_username(username)
                .enter_password(password)
                .click_submit()
        )

    def get_error_text(self) -> str:
        """
        Wait for and return the text of the error message element.

        Returns an empty string if no error is visible within the timeout.
        """
        try:
            self.error_message.wait_for(state="visible", timeout=5_000)
            text = self.error_message.inner_text().strip()
            logger.debug(f"Error message visible: {text!r}")
            return text
        except Exception:
            logger.debug("No error message found within timeout")
            return ""

    def is_login_successful(self) -> bool:
        """
        Return True if the page shows the successful-login heading.

        This is a lightweight alternative to asserting URL changes when
        the application doesn't do a hard redirect.
        """
        try:
            self.success_heading.wait_for(state="visible", timeout=5_000)
            heading = self.success_heading.inner_text().strip()
            logger.debug(f"Post-login heading: {heading!r}")
            return "Logged In Successfully" in heading
        except Exception:
            return False

    def logout(self) -> "LoginPage":
        """Click the logout button and return self."""
        logger.info("Clicking logout")
        self.logout_button.click()
        return self
