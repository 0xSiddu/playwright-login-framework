# playwright-login-framework

A login test suite built with Playwright (Python) and pytest. I built this to practice the Page Object Model pattern and put together something clean enough to show in a QA/SDET application.

It tests against [practicetestautomation.com](https://practicetestautomation.com/practice-test-login/) — a free public demo site, so you can clone and run everything without setting up a backend.

---

## Stack

- Python 3.11+
- [Playwright for Python](https://playwright.dev/python/)
- pytest + pytest-html
- python-dotenv
- allure-pytest (optional, for a richer report UI)

---

## Project layout

```
playwright-login-framework/
├── pages/
│   ├── base_page.py      # shared helpers all pages inherit from
│   └── login_page.py     # locators + actions for the login screen
├── tests/
│   ├── conftest.py       # fixtures and failure hooks
│   └── test_login.py     # the actual test cases
├── utils/
│   ├── config.py         # reads .env and exposes a Config object
│   └── helpers.py        # screenshot capture, logging, path utils
├── reports/              # gitignored — HTML report lands here
├── screenshots/          # gitignored — failure screenshots land here
├── .env.example
├── pytest.ini
└── requirements.txt
```

---

## Getting started

```bash
git clone https://github.com/0xSiddu/playwright-login-framework.git
cd playwright-login-framework

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
playwright install chromium

cp .env.example .env
```

The defaults in `.env.example` already point at the demo site with the correct credentials, so you don't need to change anything to get the tests running.

---

## Running tests

> Make sure the virtual environment is active first (`source venv/bin/activate`). You'll see `(venv)` in your prompt. pytest is installed inside it, not globally.

```bash
# activate venv (do this once per terminal session)
source venv/bin/activate

# run everything
pytest

# watch it run in a real browser window
HEADLESS=false pytest

# just the happy-path tests
pytest tests/test_login.py::TestLoginSuccess -v

# just the negative cases
pytest tests/test_login.py::TestLoginFailure -v

# run tests in parallel
pytest -n auto

# allure report (needs allure CLI installed separately)
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

After a run, open `reports/report.html` in a browser for the full HTML report.

---

## What's being tested

**Happy path**
- Valid credentials log in successfully
- Logout button is visible after login
- URL changes after a successful login
- Logging out sends you back to the login page

**Negative cases**
- Wrong password shows an error
- Non-existent username shows an error
- Empty username field shows an error
- Empty password field shows an error
- Both fields empty shows an error
- Credentials with wrong casing or extra whitespace are rejected (5 parametrised variants)

14 tests total.

---

## On failure

If a test fails, the `context` fixture automatically:

1. Takes a full-page screenshot → `screenshots/FAIL_<testname>_<timestamp>.png`
2. Exports a Playwright trace → `reports/trace_<testname>_<timestamp>.zip`

To open a trace:

```bash
playwright show-trace reports/trace_<filename>.zip
```

It opens a timeline view where you can scrub through every action, network request, and DOM snapshot — really useful when debugging failures in CI.

---

## Configuration

Copy `.env.example` to `.env` and edit as needed.

| Variable | Default | What it does |
|---|---|---|
| `BASE_URL` | demo site URL | the login page to test against |
| `VALID_USERNAME` | `student` | credential used in happy-path tests |
| `VALID_PASSWORD` | `Password123` | credential used in happy-path tests |
| `HEADLESS` | `true` | set to `false` to watch the browser |
| `SLOW_MO` | `0` | milliseconds between actions (useful for demos) |
| `BROWSER_TIMEOUT` | `30000` | global element timeout in ms |
| `TRACE_ON_FAILURE` | `true` | export trace zip when a test fails |

---

## Notes

- Each test gets a fresh browser context (isolated cookies + storage), so tests don't bleed into each other.
- Locators live only in `pages/` — tests never touch CSS selectors directly.
- The `logged_in_page` fixture handles login as a precondition so tests that need an authenticated state don't repeat the login steps.
