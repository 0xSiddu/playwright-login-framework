"""
test_login.py — Login flow test suite.

Tests are grouped into two classes:
• TestLoginSuccess  — happy-path scenarios
• TestLoginFailure  — negative / edge-case scenarios

Each test is self-contained and independent. All browser interactions
are delegated to the LoginPage POM; tests only contain assertions and
high-level orchestration.

Target site: https://practicetestautomation.com/practice-test-login/
Valid credentials: student / Password123
"""

import logging

import pytest

from pages.login_page import LoginPage
from utils.config import config

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Happy-path tests
# ─────────────────────────────────────────────────────────────────────────────


class TestLoginSuccess:
    """Verify that valid credentials grant access to the application."""

    def test_valid_credentials_redirects_to_dashboard(self, login_page: LoginPage):
        """
        TC-001 | Valid login → successful redirect.

        Given: A user on the login page
        When:  They enter valid username and password and submit
        Then:  The page should display 'Logged In Successfully'
        """
        logger.info("TC-001 | Valid credentials — expecting success heading")

        login_page.login(config.valid_username, config.valid_password)

        # Primary assertion: success heading is visible
        assert login_page.is_login_successful(), (
            "Expected 'Logged In Successfully' heading after valid login, but it was not found."
        )
        logger.info("TC-001 | PASSED ✓")

    def test_valid_login_shows_logout_button(self, login_page: LoginPage):
        """
        TC-002 | Valid login → logout button is visible.

        Given: A user who has just logged in successfully
        When:  The post-login page is rendered
        Then:  A logout / log-out button should be visible
        """
        logger.info("TC-002 | Checking logout button visibility after login")

        login_page.login(config.valid_username, config.valid_password)

        assert login_page.is_login_successful(), "Pre-condition: login should succeed"
        assert login_page.is_visible(".wp-block-button a"), (
            "Expected a logout button to be visible after successful login."
        )
        logger.info("TC-002 | PASSED ✓")

    def test_valid_login_url_changes(self, login_page: LoginPage):
        """
        TC-003 | Valid login → URL changes to post-login page.

        Given: A user on the login page
        When:  They log in with valid credentials
        Then:  The URL should change (away from the login page)
        """
        logger.info("TC-003 | Checking URL change after valid login")

        original_url = login_page.get_current_url()
        login_page.login(config.valid_username, config.valid_password)

        assert login_page.is_login_successful(), "Pre-condition: login should succeed"

        new_url = login_page.get_current_url()
        assert new_url != original_url, (
            f"Expected URL to change after login.\n"
            f"Before: {original_url}\n"
            f"After:  {new_url}"
        )
        logger.info("TC-003 | PASSED ✓")

    def test_login_then_logout_returns_to_login_page(self, logged_in_page: LoginPage):
        """
        TC-004 | Logout → returns to login page.

        Given: A user who is already logged in (via 'logged_in_page' fixture)
        When:  They click the logout button
        Then:  They should be redirected back to the login screen
        """
        logger.info("TC-004 | Logout flow")

        logged_in_page.logout()

        # After logout we expect to land back on a page containing the login form
        assert logged_in_page.is_visible("#username"), (
            "Expected to see the username field after logout, indicating redirect to login page."
        )
        logger.info("TC-004 | PASSED ✓")


# ─────────────────────────────────────────────────────────────────────────────
# Negative / edge-case tests
# ─────────────────────────────────────────────────────────────────────────────


class TestLoginFailure:
    """Verify that invalid credentials are rejected with clear error messages."""

    def test_wrong_password_shows_error(self, login_page: LoginPage):
        """
        TC-005 | Wrong password → error message displayed.

        Given: A user on the login page
        When:  They enter a valid username with an incorrect password
        Then:  An error message should be shown and login should fail
        """
        logger.info("TC-005 | Wrong password — expecting error message")

        login_page.login(config.valid_username, "WrongPassword!")
        error_text = login_page.get_error_text()

        assert error_text, "Expected an error message but none was displayed."
        assert "password" in error_text.lower() or "incorrect" in error_text.lower(), (
            f"Error message does not mention 'password' or 'incorrect'.\n"
            f"Actual error: {error_text!r}"
        )
        assert not login_page.is_login_successful(), (
            "Login should NOT succeed with a wrong password."
        )
        logger.info(f"TC-005 | PASSED ✓ (error: {error_text!r})")

    def test_invalid_username_shows_error(self, login_page: LoginPage):
        """
        TC-006 | Invalid username → error message displayed.

        Given: A user on the login page
        When:  They enter a non-existent username with any password
        Then:  An error message should be shown and login should fail
        """
        logger.info("TC-006 | Invalid username — expecting error message")

        login_page.login("nonexistent_user_xyz", config.valid_password)
        error_text = login_page.get_error_text()

        assert error_text, "Expected an error message but none was displayed."
        assert not login_page.is_login_successful(), (
            "Login should NOT succeed with an invalid username."
        )
        logger.info(f"TC-006 | PASSED ✓ (error: {error_text!r})")

    def test_empty_username_shows_error(self, login_page: LoginPage):
        """
        TC-007 | Empty username → error message displayed.

        Given: A user on the login page
        When:  They leave the username field blank and submit
        Then:  An error message should be shown
        """
        logger.info("TC-007 | Empty username field — expecting error message")

        login_page.login("", config.valid_password)
        error_text = login_page.get_error_text()

        assert error_text, (
            "Expected an error message when username is empty, but none was shown."
        )
        assert not login_page.is_login_successful(), (
            "Login should NOT succeed with an empty username."
        )
        logger.info(f"TC-007 | PASSED ✓ (error: {error_text!r})")

    def test_empty_password_shows_error(self, login_page: LoginPage):
        """
        TC-008 | Empty password → error message displayed.

        Given: A user on the login page
        When:  They leave the password field blank and submit
        Then:  An error message should be shown
        """
        logger.info("TC-008 | Empty password field — expecting error message")

        login_page.login(config.valid_username, "")
        error_text = login_page.get_error_text()

        assert error_text, (
            "Expected an error message when password is empty, but none was shown."
        )
        assert not login_page.is_login_successful(), (
            "Login should NOT succeed with an empty password."
        )
        logger.info(f"TC-008 | PASSED ✓ (error: {error_text!r})")

    def test_both_fields_empty_shows_error(self, login_page: LoginPage):
        """
        TC-009 | Both fields empty → error message displayed.

        Given: A user on the login page
        When:  They submit the form with both fields blank
        Then:  An error message should be shown
        """
        logger.info("TC-009 | Both fields empty — expecting error message")

        login_page.login("", "")
        error_text = login_page.get_error_text()

        assert error_text, (
            "Expected an error message when both fields are empty, but none was shown."
        )
        assert not login_page.is_login_successful(), (
            "Login should NOT succeed with both fields empty."
        )
        logger.info(f"TC-009 | PASSED ✓ (error: {error_text!r})")

    @pytest.mark.parametrize("username,password,description", [
        ("student", "password123",   "lowercase password"),
        ("Student", "Password123",   "uppercase first letter in username"),
        ("student ", "Password123",  "trailing space in username"),
        (" student", "Password123",  "leading space in username"),
        ("student", "Password123 ",  "trailing space in password"),
    ])
    def test_case_and_whitespace_sensitivity(
        self,
        login_page: LoginPage,
        username: str,
        password: str,
        description: str,
    ):
        """
        TC-010 | Credential case / whitespace sensitivity.

        Given: A user on the login page
        When:  They enter credentials that differ in case or whitespace
        Then:  Login should fail (credentials must match exactly)
        """
        logger.info(f"TC-010 | Variant: {description}")

        login_page.login(username, password)

        # Re-open login page between parametrize iterations when login fails
        # (the page stays on login after failed attempt — no action needed)
        is_success = login_page.is_login_successful()

        # NOTE: This assertion documents the *expected* strict behaviour.
        # If the target app accepts case-insensitive logins, update accordingly.
        assert not is_success, (
            f"Login should NOT succeed with variant '{description}' "
            f"(username={username!r}, password=***)"
        )
        logger.info(f"TC-010 | PASSED ✓ ({description})")
