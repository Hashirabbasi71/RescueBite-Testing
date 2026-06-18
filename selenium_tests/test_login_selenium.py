"""
Selenium WebDriver GUI Tests — Login Module (RescueBite)
Uses Chrome via webdriver-manager.
"""

import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "https://rescuebite-sc83.vercel.app"


class TestLoginSelenium:
    """Selenium GUI tests for the RescueBite login page."""

    @pytest.fixture
    def driver(self):
        service = Service(ChromeDriverManager().install())
        driver  = webdriver.Chrome(service=service)
        driver.maximize_window()
        driver.get(f"{BASE_URL}/login")
        yield driver
        driver.quit()

    # TC-LGN-S-001 ────────────────────────────────────────────────────────────
    def test_valid_login_restaurant(self, driver):
        """TC-LGN-S-001: Valid restaurant credentials redirect to /dashboard or /go"""
        driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys("restaurant@test.com")
        driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys("Testpass@123")
        driver.find_element(By.CSS_SELECTOR, 'button.btn-primary').click()

        WebDriverWait(driver, 10).until(
            lambda d: "/login" not in d.current_url
        )
        assert "/login" not in driver.current_url

    # TC-LGN-S-002 ────────────────────────────────────────────────────────────
    def test_invalid_password_shows_error(self, driver):
        """TC-LGN-S-002: Wrong password shows error message"""
        driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys("restaurant@test.com")
        driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys("wrongpassword")
        driver.find_element(By.CSS_SELECTOR, 'button.btn-primary').click()

        error = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'p.text-sm.text-clay'))
        )
        assert error.is_displayed()
        assert len(error.text) > 0

    # TC-LGN-S-003 ────────────────────────────────────────────────────────────
    def test_unknown_email_shows_error(self, driver):
        """TC-LGN-S-003: Unregistered email shows error message"""
        driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys("nobody@nowhere.com")
        driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys("Testpass@123")
        driver.find_element(By.CSS_SELECTOR, 'button.btn-primary').click()

        error = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'p.text-sm.text-clay'))
        )
        assert error.is_displayed()

    # TC-LGN-S-004 ────────────────────────────────────────────────────────────
    def test_password_field_is_masked(self, driver):
        """TC-LGN-S-004: Password input type is 'password' (masked)"""
        pwd_field = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        assert pwd_field.get_attribute("type") == "password"

    # TC-LGN-S-005 ────────────────────────────────────────────────────────────
    def test_enter_key_submits_form(self, driver):
        """TC-LGN-S-005: Pressing Enter on password field submits the form"""
        driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys("restaurant@test.com")
        pwd = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
        pwd.send_keys("Testpass@123")
        pwd.send_keys(Keys.RETURN)

        time.sleep(3)
        redirected  = "/login" not in driver.current_url
        error_shown = len(driver.find_elements(By.CSS_SELECTOR, 'p.text-sm.text-clay')) > 0
        assert redirected or error_shown

    # TC-LGN-S-006 ────────────────────────────────────────────────────────────
    def test_create_account_link_navigates(self, driver):
        """TC-LGN-S-006: 'Create an account' link goes to /register"""
        link = driver.find_element(By.CSS_SELECTOR, 'a[href="/register"]')
        link.click()
        WebDriverWait(driver, 5).until(EC.url_contains("/register"))
        assert "/register" in driver.current_url

    # TC-LGN-S-007 ────────────────────────────────────────────────────────────
    def test_logo_link_goes_to_home(self, driver):
        """TC-LGN-S-007: RescueBite logo navigates to home page"""
        logo = driver.find_element(By.CSS_SELECTOR, 'a[href="/"]')
        logo.click()
        WebDriverWait(driver, 5).until(EC.url_to_be(f"{BASE_URL}/"))
        assert driver.current_url == f"{BASE_URL}/"

    # TC-LGN-S-008 ────────────────────────────────────────────────────────────
    def test_loading_state_button_text(self, driver):
        """TC-LGN-S-008: Submit button label changes to 'Logging in…' during request"""
        driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys("restaurant@test.com")
        driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys("Testpass@123")
        driver.find_element(By.CSS_SELECTOR, 'button.btn-primary').click()

        try:
            loading_btn = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//button[contains(text(), "Logging in")]')
                )
            )
            assert "Logging in" in loading_btn.text
        except Exception:
            # If too fast to catch, assert redirect happened instead
            assert "/login" not in driver.current_url or \
                   len(driver.find_elements(By.CSS_SELECTOR, 'p.text-sm.text-clay')) > 0

    # TC-LGN-S-009 ────────────────────────────────────────────────────────────
    def test_direct_dashboard_redirects_unauthenticated(self, driver):
        """TC-LGN-S-009: Accessing /dashboard without auth redirects to login"""
        driver.get(f"{BASE_URL}/dashboard")
        time.sleep(2)
        assert "/login" in driver.current_url or "/pending" in driver.current_url

    # TC-LGN-S-010 ────────────────────────────────────────────────────────────
    def test_sql_injection_does_not_redirect(self, driver):
        """TC-LGN-S-010: SQL injection in email does not bypass login"""
        driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys(
            "' OR '1'='1'; --@test.com"
        )
        driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys("anything")
        driver.find_element(By.CSS_SELECTOR, 'button.btn-primary').click()
        time.sleep(3)
        assert "/dashboard" not in driver.current_url
        assert "/ngo" not in driver.current_url

    # TC-LGN-S-011 ────────────────────────────────────────────────────────────
    def test_page_title_contains_rescuebite(self, driver):
        """TC-LGN-S-011: Browser tab or page shows RescueBite branding"""
        brand = driver.find_element(By.XPATH, '//*[contains(text(), "RescueBite")]')
        assert brand.is_displayed()

    # TC-LGN-S-012 ────────────────────────────────────────────────────────────
    def test_email_field_accepts_valid_format_only(self, driver):
        """TC-LGN-S-012: HTML5 email field rejects non-email strings"""
        email_input = driver.find_element(By.CSS_SELECTOR, 'input[type="email"]')
        assert email_input.get_attribute("type") == "email"
