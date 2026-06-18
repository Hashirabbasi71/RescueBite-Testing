"""
conftest.py — shared Playwright fixtures for RescueBite test suite
"""

import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "https://rescuebite-sc83.vercel.app"

# ── Credentials ────────────────────────────────────────────────────────────────
TEST_RESTAURANT_EMAIL    = "restaurant@test.com"
TEST_RESTAURANT_PASSWORD = "Testpass@123"
TEST_NGO_EMAIL           = "ngo@test.com"
TEST_NGO_PASSWORD        = "Testpass@123"
TEST_ADMIN_EMAIL         = "admin@rescuebite.com"
TEST_ADMIN_PASSWORD      = "adminpass123"


@pytest.fixture(scope="session")
def browser_instance():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        yield browser
        browser.close()


@pytest.fixture
def page(browser_instance):
    context = browser_instance.new_context()
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def restaurant_page(browser_instance):
    """Page already logged in as a restaurant user."""
    context = browser_instance.new_context()
    page = context.new_page()
    page.goto(f"{BASE_URL}/login")
    page.fill('input[type="email"]', TEST_RESTAURANT_EMAIL)
    page.fill('input[type="password"]', TEST_RESTAURANT_PASSWORD)
    page.locator('button:has-text("Log in")').click()
    # App redirects /go → /dashboard; wait for login to leave /login
    page.wait_for_url(f"{BASE_URL}/**", timeout=15000)
    page.wait_for_url(lambda url: "/login" not in url, timeout=15000)
    yield page
    context.close()


@pytest.fixture
def ngo_page(browser_instance):
    """Page already logged in as an NGO user."""
    context = browser_instance.new_context()
    page = context.new_page()
    page.goto(f"{BASE_URL}/login")
    page.fill('input[type="email"]', TEST_NGO_EMAIL)
    page.fill('input[type="password"]', TEST_NGO_PASSWORD)
    page.locator('button:has-text("Log in")').click()
    page.wait_for_url(f"{BASE_URL}/**", timeout=15000)
    page.wait_for_url(lambda url: "/login" not in url, timeout=15000)
    yield page
    context.close()
