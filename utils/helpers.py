"""
helpers.py — Reusable utility functions for the framework.

Provides screenshot capture, logging configuration, directory
management, and any other cross-cutting concerns.
"""

import logging
import os
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page

from utils.config import config

# ── Logging setup ─────────────────────────────────────────────────────────────

def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure root logger with a consistent format.
    Call once at session start (done inside conftest.py).
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


logger = logging.getLogger(__name__)


# ── Directory helpers ─────────────────────────────────────────────────────────

def ensure_dir(path: str | Path) -> Path:
    """Create *path* (and parents) if it doesn't exist, then return it."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


# ── Screenshot helpers ────────────────────────────────────────────────────────

def take_screenshot(page: Page, name: str) -> Path:
    """
    Capture a full-page screenshot and save it to the screenshots directory.

    Args:
        page:  The Playwright Page object.
        name:  A descriptive filename stem (no extension needed).

    Returns:
        The resolved Path of the saved screenshot.
    """
    screenshots_dir = ensure_dir(config.screenshot_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Sanitise name so it is safe as a filename
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    file_path = screenshots_dir / f"{safe_name}_{timestamp}.png"

    page.screenshot(path=str(file_path), full_page=True)
    logger.info(f"Screenshot saved → {file_path}")
    return file_path


def take_failure_screenshot(page: Page, test_name: str) -> Path:
    """
    Convenience wrapper: take a screenshot tagged as a failure.

    Args:
        page:       The Playwright Page object.
        test_name:  The name of the failing test.

    Returns:
        The resolved Path of the saved screenshot.
    """
    return take_screenshot(page, f"FAIL_{test_name}")


# ── Trace helpers ─────────────────────────────────────────────────────────────

def save_trace(context, test_name: str) -> Path:
    """
    Stop Playwright tracing and export the trace to the reports directory.

    Args:
        context:    A Playwright BrowserContext that was started with tracing.
        test_name:  Name of the test (used in the filename).

    Returns:
        The resolved Path of the saved trace.
    """
    report_dir = ensure_dir(config.report_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in test_name)
    trace_path = report_dir / f"trace_{safe_name}_{timestamp}.zip"

    context.tracing.stop(path=str(trace_path))
    logger.info(f"Trace saved → {trace_path}")
    logger.info("  View with: playwright show-trace %s", trace_path)
    return trace_path


# ── Misc ──────────────────────────────────────────────────────────────────────

def get_timestamp() -> str:
    """Return a sortable timestamp string (e.g. '2024-06-14_18-45-00')."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
