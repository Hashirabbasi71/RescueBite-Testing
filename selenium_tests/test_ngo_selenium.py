"""
Selenium WebDriver GUI Tests — NGO Module (RescueBite)
Covers /ngo (discover) and /ngo/claims pages.
"""

import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL        = "https://rescuebite-sc83.vercel.app"
NGO_EMAIL       = "ngo@test.com"
NGO_PASSWORD    = "Testpass@123"


def _login_ngo(driver):
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys(NGO_EMAIL)
    driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys(NGO_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, 'button.btn-primary').click()
    WebDriverWait(driver, 10).until(lambda d: "/login" not in d.current_url)


class TestNgoDiscoverSelenium:
    """Selenium tests for the NGO food discovery page."""

    @pytest.fixture
    def driver(self):
        service = Service(ChromeDriverManager().install())
        driver  = webdriver.Chrome(service=service)
        driver.maximize_window()
        _login_ngo(driver)
        driver.get(f"{BASE_URL}/ngo")
        yield driver
        driver.quit()

    # TC-NGO-S-001 ────────────────────────────────────────────────────────────
    def test_discover_page_loads(self, driver):
        """TC-NGO-S-001: NGO discover page loads and shows heading"""
        heading = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))
        )
        assert heading.is_displayed()
        assert len(heading.text) > 0

    # TC-NGO-S-002 ────────────────────────────────────────────────────────────
    def test_stat_cards_present(self, driver):
        """TC-NGO-S-002: At least 3 stat cards are visible on the discover page"""
        stat_cards = driver.find_elements(By.CSS_SELECTOR, '.stat-card')
        assert len(stat_cards) >= 3

    # TC-NGO-S-003 ────────────────────────────────────────────────────────────
    def test_base_location_displayed(self, driver):
        """TC-NGO-S-003: Base location indicator is shown on the page"""
        base_label = driver.find_element(By.XPATH, '//*[contains(text(), "Base:")]')
        assert base_label.is_displayed()

    # TC-NGO-S-004 ────────────────────────────────────────────────────────────
    def test_unauthenticated_access_redirects(self, driver):
        """TC-NGO-S-004: Accessing /ngo without auth redirects to login"""
        # Open a new private window to simulate unauthenticated state
        driver.execute_script("window.open('about:blank', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(f"{BASE_URL}/ngo")
        time.sleep(2)
        assert "/login" in driver.current_url or "/pending" in driver.current_url


class TestNgoClaimsSelenium:
    """Selenium tests for the NGO claims page."""

    @pytest.fixture
    def driver(self):
        service = Service(ChromeDriverManager().install())
        driver  = webdriver.Chrome(service=service)
        driver.maximize_window()
        _login_ngo(driver)
        driver.get(f"{BASE_URL}/ngo/claims")
        yield driver
        driver.quit()

    # TC-CLM-S-001 ────────────────────────────────────────────────────────────
    def test_claims_page_loads(self, driver):
        """TC-CLM-S-001: Claims page loads and shows heading"""
        heading = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))
        )
        assert heading.is_displayed()

    # TC-CLM-S-002 ────────────────────────────────────────────────────────────
    def test_stat_cards_present(self, driver):
        """TC-CLM-S-002: Stats cards visible (Claims, Active, Collected)"""
        stat_cards = driver.find_elements(By.CSS_SELECTOR, '.stat-card')
        assert len(stat_cards) >= 3

    # TC-CLM-S-003 ────────────────────────────────────────────────────────────
    def test_empty_state_or_claims_shown(self, driver):
        """TC-CLM-S-003: Page shows either empty-state message or claim cards"""
        empty_texts = driver.find_elements(
            By.XPATH, '//*[contains(text(), "haven\'t claimed")]'
        )
        claim_cards = driver.find_elements(By.CSS_SELECTOR, '.card')
        assert len(empty_texts) > 0 or len(claim_cards) > 0

    # TC-CLM-S-004 ────────────────────────────────────────────────────────────
    def test_directions_links_use_google_maps(self, driver):
        """TC-CLM-S-004: Directions links point to Google Maps"""
        dir_links = driver.find_elements(By.XPATH, '//a[contains(text(), "Directions")]')
        for link in dir_links:
            href = link.get_attribute("href")
            assert "google.com/maps" in href, \
                f"Expected Google Maps URL, got: {href}"

    # TC-CLM-S-005 ────────────────────────────────────────────────────────────
    def test_collection_code_format(self, driver):
        """TC-CLM-S-005: Collection codes displayed are 6 uppercase alphanumeric chars"""
        import re
        # Find any displayed collection codes
        code_elements = driver.find_elements(
            By.CSS_SELECTOR, '.font-display'
        )
        for el in code_elements:
            text = el.text.strip()
            if len(text) == 6:
                assert re.fullmatch(r'[A-Z0-9]{6}', text), \
                    f"Code '{text}' does not match expected format"

    # TC-CLM-S-006 ────────────────────────────────────────────────────────────
    def test_hero_pill_label_visible(self, driver):
        """TC-CLM-S-006: 'My claims' hero pill is visible"""
        pill = driver.find_element(By.XPATH, '//*[contains(text(), "My claims")]')
        assert pill.is_displayed()
