"""
conftest.py — Session-scoped and function-scoped fixtures.

pytest discovers this file automatically. All fixtures defined here are
available to every test without explicit imports.
"""

import logging
import os
from pathlib import Path
from typing import Generator

import pytest
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)

from pages.login_page import LoginPage
from utils.config import config
from utils.helpers import (
    ensure_dir,
    save_trace,
    setup_logging,
    take_failure_screenshot,
)

# ── One-time logging configuration ───────────────────────────────────────────
setup_logging(logging.INFO)
logger = logging.getLogger(__name__)

# ── Ensure output directories exist ──────────────────────────────────────────
ensure_dir(config.screenshot_dir)
ensure_dir(config.report_dir)


# ─────────────────────────────────────────────────────────────────────────────
# Session-scoped: Playwright instance + Browser
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    """
    Start a single Playwright process for the entire test session.

    Using session scope avoids the overhead of launching/stopping
    Playwright for every individual test.
    """
    logger.info("Starting Playwright session")
    config.log_summary()
    with sync_playwright() as pw:
        yield pw
    logger.info("Playwright session ended")


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Generator[Browser, None, None]:
    """
    Launch a single Chromium browser for the entire session.

    Headed / headless mode is controlled by the HEADLESS env variable.
    ``slow_mo`` adds a delay between actions — handy for demos.
    """
    logger.info(
        f"Launching Chromium | headless={config.headless} | slow_mo={config.slow_mo}"
    )
    b = playwright_instance.chromium.launch(
        headless=config.headless,
        slow_mo=config.slow_mo,
    )
    yield b
    logger.info("Closing browser")
    b.close()


# ─────────────────────────────────────────────────────────────────────────────
# Function-scoped: Context + Page (one fresh context per test)
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="function")
def context(browser: Browser, request: pytest.FixtureRequest) -> Generator[BrowserContext, None, None]:
    """
    Create a fresh BrowserContext for every test.

    • Tracing is started automatically when TRACE_ON_FAILURE=true.
    • On failure, the trace is exported and a screenshot is taken.
    • The context (and its cookies/storage) is destroyed after each test.
    """
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 800},
        record_video_dir=None,  # Enable if you want video: set to str(config.report_dir)
    )

    # Start Playwright trace if configured
    if config.trace_on_failure:
        ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
        logger.debug("Tracing started for this context")

    yield ctx

    # ── Teardown: capture artefacts on failure ────────────────────────────────
    test_failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False

    if test_failed:
        test_name = request.node.name
        logger.warning(f"Test FAILED: {test_name}. Capturing artefacts…")

        # Screenshot
        pages = ctx.pages
        if pages:
            take_failure_screenshot(pages[-1], test_name)

        # Trace
        if config.trace_on_failure:
            save_trace(ctx, test_name)
    else:
        # Stop tracing without saving to keep disk clean
        if config.trace_on_failure:
            ctx.tracing.stop()

    ctx.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """
    Open a single Page inside the per-test BrowserContext.

    Using this fixture (rather than browser.new_page()) ensures every
    test starts with a clean cookie jar and localStorage.
    """
    p = context.new_page()
    p.set_default_timeout(config.browser_timeout)
    yield p
    p.close()


# ─────────────────────────────────────────────────────────────────────────────
# Page Object fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture(scope="function")
def login_page(page: Page) -> LoginPage:
    """
    Return a LoginPage instance and navigate to the login URL.

    Tests that need to start on the login screen should use this
    fixture instead of calling LoginPage(page).open() manually.
    """
    lp = LoginPage(page)
    lp.open()
    return lp


@pytest.fixture(scope="function")
def logged_in_page(login_page: LoginPage) -> LoginPage:
    """
    Return a LoginPage after performing a successful login.

    Use this fixture for tests that require an authenticated session
    but don't need to test the login flow itself.
    """
    login_page.login(config.valid_username, config.valid_password)
    assert login_page.is_login_successful(), (
        "Pre-condition failed: could not log in with valid credentials. "
        "Check BASE_URL / VALID_USERNAME / VALID_PASSWORD in .env"
    )
    return login_page


# ─────────────────────────────────────────────────────────────────────────────
# pytest hooks
# ─────────────────────────────────────────────────────────────────────────────


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Attach the test outcome to ``request.node`` so teardown fixtures
    can check whether a test passed or failed.

    This hook is the standard pattern for accessing test status inside
    fixtures — see https://docs.pytest.org/en/stable/how-to/fixtures.html
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
