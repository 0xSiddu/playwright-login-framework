"""
config.py — Central configuration module.

Loads environment variables from .env (via dotenv) and exposes a
typed `Config` object used throughout the framework.
"""

import os
import logging
from dataclasses import dataclass, field
from dotenv import load_dotenv

# ── Load .env file (silently ignored if absent) ──────────────────────────────
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Config:
    """Immutable configuration loaded from environment variables."""

    # ── Target environment ────────────────────────────────────────────────────
    env: str = field(default_factory=lambda: os.getenv("ENV", "dev"))
    base_url: str = field(default_factory=lambda: os.getenv(
        "BASE_URL", "https://practicetestautomation.com/practice-test-login/"
    ))

    # ── Valid test credentials (from .env) ────────────────────────────────────
    valid_username: str = field(
        default_factory=lambda: os.getenv("VALID_USERNAME", "student")
    )
    valid_password: str = field(
        default_factory=lambda: os.getenv("VALID_PASSWORD", "Password123")
    )

    # ── Browser / execution settings ─────────────────────────────────────────
    headless: bool = field(
        default_factory=lambda: os.getenv("HEADLESS", "true").lower() == "true"
    )
    slow_mo: int = field(
        default_factory=lambda: int(os.getenv("SLOW_MO", "0"))
    )
    browser_timeout: int = field(
        default_factory=lambda: int(os.getenv("BROWSER_TIMEOUT", "30000"))
    )

    # ── Reporting ─────────────────────────────────────────────────────────────
    screenshot_dir: str = field(
        default_factory=lambda: os.getenv("SCREENSHOT_DIR", "screenshots")
    )
    report_dir: str = field(
        default_factory=lambda: os.getenv("REPORT_DIR", "reports")
    )
    trace_on_failure: bool = field(
        default_factory=lambda: os.getenv("TRACE_ON_FAILURE", "true").lower() == "true"
    )

    def log_summary(self) -> None:
        """Log a summary of active configuration (masks password)."""
        logger.info("=" * 55)
        logger.info("  Framework Configuration")
        logger.info("=" * 55)
        logger.info(f"  ENV          : {self.env}")
        logger.info(f"  BASE_URL     : {self.base_url}")
        logger.info(f"  HEADLESS     : {self.headless}")
        logger.info(f"  SLOW_MO      : {self.slow_mo}ms")
        logger.info(f"  TIMEOUT      : {self.browser_timeout}ms")
        logger.info(f"  SCREENSHOT   : ./{self.screenshot_dir}")
        logger.info(f"  REPORTS      : ./{self.report_dir}")
        logger.info("=" * 55)


# Singleton — import this everywhere instead of constructing per-call
config = Config()
