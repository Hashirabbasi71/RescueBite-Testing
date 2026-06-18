# How to Run RescueBite Tests

## 1. Prerequisites

Make sure you have **Python 3.9+** installed.

```bash
python --version
```

---

## 2. Install Dependencies

Open a terminal inside the `RescueBite_Testing_Project` folder and run:

```bash
pip install -r requirements.txt
```

Then install Playwright's browser binaries:

```bash
playwright install chromium
```

---

## 3. Start the RescueBite App

The tests expect the app running at `https://rescuebite-sc83.vercel.app`.  
Open a **separate terminal** in the root project folder and run:

```bash
npm run dev
```

Keep it running while you execute the tests.

---

## 4. Set Up Test Accounts

Before running browser tests, make sure these two accounts exist in your Supabase database:

| Role       | Email                    | Password      |
|------------|--------------------------|---------------|
| RESTAURANT | restaurant@test.com      | Testpass@123   |
| NGO        | ngo@test.com             | Testpass@123   |

Register them manually via `https://rescuebite-sc83.vercel.app/register` and approve them in the admin panel.

---

## 5. Run All Tests

```bash
python -m pytest -v
```

> If `pytest` alone gives "not recognized", always use `python -m pytest` — this happens when pip installs to the user directory and the Scripts folder is not in PATH.

---

## 6. Run Specific Test Groups

### Unit Tests only (no browser, runs instantly)

```bash
pytest unit_tests/ -v
```

### Data-Driven Playwright Tests only

```bash
pytest tests/ -v
```

### Selenium GUI Tests only

```bash
pytest selenium_tests/ -v
```

---

## 7. Run a Single Test File

```bash
# Login unit tests
pytest unit_tests/test_login_unit.py -v

# Donation unit tests
pytest unit_tests/test_donation_unit.py -v

# Claim unit tests
pytest unit_tests/test_claim_unit.py -v

# Login Playwright tests
pytest tests/test_login.py -v

# Register Playwright tests
pytest tests/test_register.py -v

# Donation Playwright tests
pytest tests/test_donation.py -v

# Login Selenium tests
pytest selenium_tests/test_login_selenium.py -v

# Donation Selenium tests
pytest selenium_tests/test_donation_selenium.py -v

# NGO Selenium tests
pytest selenium_tests/test_ngo_selenium.py -v
```

---

## 8. Run Tests by Marker

Tests are tagged with markers. You can filter by category:

```bash
# Only positive/happy-path tests
pytest -m positive -v

# Only negative/error-path tests
pytest -m negative -v

# Only boundary/edge-value tests
pytest -m boundary -v

# Only security tests
pytest -m security -v
```

---

## 9. Run Tests in Parallel (Faster)

Install the parallel plugin first:

```bash
pip install pytest-xdist
```

Then run with multiple workers:

```bash
pytest -n 4
```

> Note: Do not run Selenium tests in parallel — each one opens its own Chrome window and they may conflict.

---

## 10. Generate an HTML Report

Install the report plugin:

```bash
pip install pytest-html
```

Run with report output:

```bash
pytest --html=report.html --self-contained-html
```

Open `report.html` in your browser to see results.

---

## 11. Common Errors and Fixes

| Error | Fix |
|---|---|
| `ModuleNotFoundError: playwright` | Run `pip install -r requirements.txt` |
| `Browser not found` | Run `playwright install chromium` |
| `Connection refused rescuebite-sc83.vercel.app` | Check your internet connection or Vercel deployment status |
| `Invalid login credentials` in browser tests | Create test accounts in Supabase and approve them |
| `WebDriverException: ChromeDriver not found` | webdriver-manager installs it automatically — just run again |
| `FileNotFoundError: test_data/login_test_data.xml` | Run pytest from inside the `RescueBite_Testing_Project` folder |

---

## 12. Quick Reference

```
RescueBite_Testing_Project/
├── unit_tests/          ← Pure Python, no browser needed
│   ├── test_login_unit.py      (18 tests)
│   ├── test_donation_unit.py   (18 tests)
│   └── test_claim_unit.py      (15 tests)
├── tests/               ← Playwright browser tests (data-driven from XML)
│   ├── test_login.py           (10+ tests)
│   ├── test_register.py        (10+ tests)
│   └── test_donation.py        (10+ tests)
├── selenium_tests/      ← Selenium Chrome GUI tests
│   ├── test_login_selenium.py  (12 tests)
│   ├── test_donation_selenium.py (10 tests)
│   └── test_ngo_selenium.py    (10 tests)
├── test_data/           ← XML test data files
├── pages/               ← Page Object Model classes
├── utils/               ← XML parser utility
├── conftest.py          ← Shared fixtures
├── pytest.ini           ← pytest configuration
└── requirements.txt     ← Python dependencies
```
