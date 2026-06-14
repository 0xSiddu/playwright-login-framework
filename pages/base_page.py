"""
base_page.py — BasePage class.

All page objects inherit from this class, which wraps common Playwright
actions with sensible defaults and built-in logging.
"""

import logging
from typing import Optional

from playwright.sync_api import Page, Locator, expect

from utils.config import config

logger = logging.getLogger(__name__)


class BasePage:
    """
    Base class for all Page Object Model (POM) pages.

    Wraps raw Playwright API calls with:
    • Unified timeout from config
    • Debug-level action logging
    • Helper methods for common UI interactions
    """

    def __init__(self, page: Page) -> None:
        self.page = page
        self.timeout = config.browser_timeout  # default timeout (ms)

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate(self, url: str) -> None:
        """Navigate to *url* and wait until the network is idle."""
        logger.debug(f"Navigating to: {url}")
        self.page.goto(url, wait_until="networkidle")

    def get_current_url(self) -> str:
        """Return the current page URL."""
        return self.page.url

    def get_page_title(self) -> str:
        """Return the current page <title>."""
        return self.page.title()

    def reload(self) -> None:
        """Reload the current page."""
        logger.debug("Reloading page")
        self.page.reload(wait_until="networkidle")

    # ── Element interactions ──────────────────────────────────────────────────

    def click(self, selector: str, timeout: Optional[int] = None) -> None:
        """
        Click an element identified by *selector*.

        Playwright auto-waits for the element to be visible + enabled
        before clicking.
        """
        t = timeout or self.timeout
        logger.debug(f"Clicking: {selector}")
        self.page.click(selector, timeout=t)

    def fill(self, selector: str, text: str, timeout: Optional[int] = None) -> None:
        """
        Clear the input at *selector* and type *text*.

        Prefer ``fill`` over ``type`` for form inputs — it's faster and
        properly triggers change events.
        """
        t = timeout or self.timeout
        logger.debug(f"Filling '{selector}' with value (length={len(text)})")
        self.page.fill(selector, text, timeout=t)

    def clear_and_fill(self, selector: str, text: str) -> None:
        """Triple-click to select all, then fill (safe for pre-populated inputs)."""
        self.page.triple_click(selector)
        self.page.fill(selector, text)

    def get_text(self, selector: str, timeout: Optional[int] = None) -> str:
        """Return the inner text of the element at *selector*."""
        t = timeout or self.timeout
        return self.page.inner_text(selector, timeout=t).strip()

    def is_visible(self, selector: str, timeout: Optional[int] = None) -> bool:
        """Return True if the element is visible within *timeout* ms."""
        t = timeout or self.timeout
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=t)
            return True
        except Exception:
            return False

    def wait_for_url(self, pattern: str, timeout: Optional[int] = None) -> None:
        """Wait until the page URL contains *pattern*."""
        t = timeout or self.timeout
        logger.debug(f"Waiting for URL to contain: {pattern}")
        self.page.wait_for_url(f"**{pattern}**", timeout=t)

    # ── Assertions (thin wrappers around Playwright's expect) ─────────────────

    def assert_visible(self, locator: Locator, message: str = "") -> None:
        """Assert that *locator* is visible."""
        expect(locator).to_be_visible(timeout=self.timeout)

    def assert_text(self, locator: Locator, text: str) -> None:
        """Assert that *locator* contains *text*."""
        expect(locator).to_contain_text(text, timeout=self.timeout)
