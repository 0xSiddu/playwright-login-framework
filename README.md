# 🎭 playwright-login-framework

> A professional, production-quality **Playwright + pytest** automation framework
> demonstrating a complete **Login flow** test suite — built with QA/SDET best practices.

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue?logo=python)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/playwright-1.44-green?logo=playwright)](https://playwright.dev/python/)
[![pytest](https://img.shields.io/badge/pytest-8.x-orange?logo=pytest)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

---

## 📐 Architecture

```
playwright-login-framework/
├── tests/
│   ├── conftest.py         # Fixtures: browser, context, page, login_page, logged_in_page
│   └── test_login.py       # 9 named TCs + 5 parametrised variants (TC-001 → TC-010)
├── pages/
│   ├── base_page.py        # BasePage: shared Playwright helpers + auto-logging
│   └── login_page.py       # LoginPage POM: locators as @property, chainable actions
├── utils/
│   ├── config.py           # Typed Config dataclass loaded from .env
│   └── helpers.py          # Screenshot, trace, logging, directory utilities
├── reports/                # ← gitignored  (HTML report + pytest log + trace zips)
├── screenshots/            # ← gitignored  (failure screenshots)
├── .env.example            # Template for all supported environment variables
├── pytest.ini              # Test discovery, markers, HTML report, CLI logging
├── requirements.txt        # Pinned runtime + optional dev dependencies
└── .gitignore
```

---

## 🚀 Quick Start

### 1 — Clone & create a virtual environment

```bash
git clone https://github.com/YOUR_HANDLE/playwright-login-framework.git
cd playwright-login-framework

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2 — Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium      # download Chromium browser binary
```

### 3 — Configure environment

```bash
cp .env.example .env
# Edit .env if you need to change BASE_URL or credentials
```

### 4 — Run the tests

```bash
# Default (headless, HTML report generated in reports/)
pytest

# Watch the browser — set HEADLESS=false in .env, or:
HEADLESS=false pytest

# Single test class
pytest tests/test_login.py::TestLoginSuccess -v

# Single test
pytest tests/test_login.py::TestLoginFailure::test_wrong_password_shows_error -v

# Smoke tests only
pytest -m smoke

# Parallel execution (requires pytest-xdist)
pytest -n auto

# Allure report (requires Allure CLI installed)
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

---

## 🧪 Test Cases

| ID     | Class              | Scenario                                        | Expected Outcome           |
|--------|--------------------|-------------------------------------------------|----------------------------|
| TC-001 | `TestLoginSuccess` | Valid username + password                       | "Logged In Successfully"   |
| TC-002 | `TestLoginSuccess` | Valid login → logout button visible             | Logout CTA is visible      |
| TC-003 | `TestLoginSuccess` | Valid login → URL changes                       | URL differs from login URL |
| TC-004 | `TestLoginSuccess` | Logout → redirects back to login page           | Username field visible     |
| TC-005 | `TestLoginFailure` | Valid username + **wrong** password             | Error message shown        |
| TC-006 | `TestLoginFailure` | **Invalid** username + valid password           | Error message shown        |
| TC-007 | `TestLoginFailure` | **Empty** username + valid password             | Error message shown        |
| TC-008 | `TestLoginFailure` | Valid username + **empty** password             | Error message shown        |
| TC-009 | `TestLoginFailure` | Both fields **empty**                           | Error message shown        |
| TC-010 | `TestLoginFailure` | 5× case/whitespace variants (parametrised)      | Login rejected each time   |

---

## 🏗️ Design Patterns & Principles

### Page Object Model (POM)
Locators live **only** in `pages/`. Tests never touch CSS selectors directly.

```python
# ✅ Good — page object handles the selector
login_page.login("student", "Password123")

# ❌ Bad — selector leaks into the test
page.fill("#username", "student")
```

### Fixture hierarchy (scope pyramid)

```
session  →  playwright_instance  →  browser
function →  context  →  page  →  login_page  →  logged_in_page
```

Each function-scoped context is **completely isolated** (no shared cookies or storage).

### Auto-artefacts on failure
The `context` fixture uses `pytest_runtest_makereport` to detect failures and automatically:
- 📸 Captures a full-page **screenshot** → `screenshots/FAIL_<test>_<timestamp>.png`
- 🔍 Exports a **Playwright trace** → `reports/trace_<test>_<timestamp>.zip`

Open a trace with:
```bash
playwright show-trace reports/trace_test_name_20240614.zip
```

---

## ⚙️ Environment Variables

| Variable           | Default                                                                | Description                        |
|--------------------|------------------------------------------------------------------------|------------------------------------|
| `ENV`              | `dev`                                                                  | Environment label (dev/staging)    |
| `BASE_URL`         | `https://practicetestautomation.com/practice-test-login/`             | Login page URL                     |
| `VALID_USERNAME`   | `student`                                                              | Username for happy-path tests      |
| `VALID_PASSWORD`   | `Password123`                                                          | Password for happy-path tests      |
| `HEADLESS`         | `true`                                                                 | Run browser headless               |
| `SLOW_MO`          | `0`                                                                    | Delay (ms) between actions         |
| `BROWSER_TIMEOUT`  | `30000`                                                                | Global element timeout (ms)        |
| `SCREENSHOT_DIR`   | `screenshots`                                                          | Directory for failure screenshots  |
| `REPORT_DIR`       | `reports`                                                              | Directory for HTML report + traces |
| `TRACE_ON_FAILURE` | `true`                                                                 | Export Playwright trace on failure |

---

## 📊 Reports

### pytest-html (built-in)
Generated automatically at `reports/report.html` on every `pytest` run.

### Allure (optional, richer UI)
```bash
# Install Allure CLI (once)
# macOS:  brew install allure
# Linux:  download from https://github.com/allure-framework/allure2/releases

pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

---

## 🧰 Tech Stack

| Tool | Version | Role |
|------|---------|------|
| [Playwright for Python](https://playwright.dev/python/) | 1.44 | Browser automation |
| [pytest](https://docs.pytest.org/) | 8.2 | Test runner + assertions |
| [pytest-html](https://pytest-html.readthedocs.io/) | 4.1 | HTML report |
| [allure-pytest](https://docs.qameta.io/allure/) | 2.13 | Rich Allure report |
| [python-dotenv](https://saurabh-kumar.com/python-dotenv/) | 1.0 | `.env` loading |
| [pytest-xdist](https://pytest-xdist.readthedocs.io/) | 3.5 | Parallel execution |
| [pytest-rerunfailures](https://github.com/pytest-dev/pytest-rerunfailures) | 14.0 | Auto-retry flaky tests |

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/my-new-tests`)
3. Follow the existing POM pattern — add locators to page objects, not tests
4. Run the full suite before opening a PR (`pytest`)
5. Open a Pull Request 🎉

---

## 📄 License

MIT © 2024 — free to use in portfolios and apprenticeship applications.
