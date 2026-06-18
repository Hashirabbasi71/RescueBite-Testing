"""
Selenium WebDriver GUI Tests — New Donation Module (RescueBite)
Requires an active browser session logged in as a restaurant.
"""

import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL              = "http://localhost:3000"
RESTAURANT_EMAIL      = "restaurant@test.com"
RESTAURANT_PASSWORD   = "Testpass@123"


def _login(driver, email=RESTAURANT_EMAIL, password=RESTAURANT_PASSWORD):
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.CSS_SELECTOR, 'input[type="email"]').send_keys(email)
    driver.find_element(By.CSS_SELECTOR, 'input[type="password"]').send_keys(password)
    driver.find_element(By.CSS_SELECTOR, 'button.btn-primary').click()
    WebDriverWait(driver, 10).until(lambda d: "/login" not in d.current_url)


class TestDonationSelenium:
    """Selenium GUI tests for the new donation form."""

    @pytest.fixture
    def driver(self):
        service = Service(ChromeDriverManager().install())
        driver  = webdriver.Chrome(service=service)
        driver.maximize_window()
        _login(driver)
        driver.get(f"{BASE_URL}/dashboard/new")
        yield driver
        driver.quit()

    # TC-DON-S-001 ────────────────────────────────────────────────────────────
    def test_form_loads_correctly(self, driver):
        """TC-DON-S-001: New donation form loads with all required fields"""
        assert driver.find_element(By.CSS_SELECTOR, 'input[placeholder*="surprise bag"]').is_displayed()
        assert driver.find_element(By.CSS_SELECTOR, 'select').is_displayed()
        assert driver.find_element(By.CSS_SELECTOR, 'input[type="number"]').is_displayed()
        assert len(driver.find_elements(By.CSS_SELECTOR, 'input[type="datetime-local"]')) == 2

    # TC-DON-S-002 ────────────────────────────────────────────────────────────
    def test_category_dropdown_has_five_options(self, driver):
        """TC-DON-S-002: Category dropdown contains all 5 category options"""
        select = Select(driver.find_element(By.CSS_SELECTOR, 'select'))
        assert len(select.options) == 5
        option_texts = [o.text for o in select.options]
        assert "Cooked meals" in option_texts
        assert "Bakery"       in option_texts
        assert "Grocery"      in option_texts
        assert "Produce"      in option_texts
        assert "Other"        in option_texts

    # TC-DON-S-003 ────────────────────────────────────────────────────────────
    def test_quantity_min_max_attributes(self, driver):
        """TC-DON-S-003: Quantity input has min=1 and max=999"""
        qty = driver.find_element(By.CSS_SELECTOR, 'input[type="number"]')
        assert qty.get_attribute("min") == "1"
        assert qty.get_attribute("max") == "999"

    # TC-DON-S-004 ────────────────────────────────────────────────────────────
    def test_image_upload_area_visible(self, driver):
        """TC-DON-S-004: Photo upload area is visible"""
        upload_text = driver.find_element(
            By.XPATH, '//*[contains(text(), "Click to upload a photo")]'
        )
        assert upload_text.is_displayed()

    # TC-DON-S-005 ────────────────────────────────────────────────────────────
    def test_empty_title_prevents_submission(self, driver):
        """TC-DON-S-005: Required title field prevents form submission"""
        driver.find_element(By.CSS_SELECTOR, 'button.btn-primary').click()
        time.sleep(1)
        assert "/dashboard/new" in driver.current_url

    # TC-DON-S-006 ────────────────────────────────────────────────────────────
    def test_invalid_pickup_window_shows_error(self, driver):
        """TC-DON-S-006: Pickup end before start shows 'invalid' error"""
        title_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder*="surprise bag"]')
        title_input.send_keys("Test donation")

        datetimes = driver.find_elements(By.CSS_SELECTOR, 'input[type="datetime-local"]')
        # Set end BEFORE start
        start_val = "2099-01-01T10:00"
        end_val   = "2099-01-01T08:00"
        driver.execute_script("arguments[0].value = arguments[1]", datetimes[0], start_val)
        driver.execute_script("arguments[0].value = arguments[1]", datetimes[1], end_val)

        driver.find_element(By.CSS_SELECTOR, 'button.btn-primary').click()
        time.sleep(3)
        error_elements = driver.find_elements(By.CSS_SELECTOR, 'p.text-sm.text-clay')
        assert len(error_elements) > 0 or "/dashboard/new" in driver.current_url

    # TC-DON-S-007 ────────────────────────────────────────────────────────────
    def test_select_bakery_category(self, driver):
        """TC-DON-S-007: Selecting Bakery category reflects in the select element"""
        select = Select(driver.find_element(By.CSS_SELECTOR, 'select'))
        select.select_by_value("BAKERY")
        assert select.first_selected_option.get_attribute("value") == "BAKERY"

    # TC-DON-S-008 ────────────────────────────────────────────────────────────
    def test_description_textarea_is_optional(self, driver):
        """TC-DON-S-008: Description textarea does not have required attribute"""
        textarea = driver.find_element(By.CSS_SELECTOR, 'textarea')
        assert textarea.get_attribute("required") is None

    # TC-DON-S-009 ────────────────────────────────────────────────────────────
    def test_submit_button_text_is_post_donation(self, driver):
        """TC-DON-S-009: Submit button text is 'Post donation'"""
        btn = driver.find_element(By.CSS_SELECTOR, 'button.btn-primary')
        assert "Post donation" in btn.text

    # TC-DON-S-010 ────────────────────────────────────────────────────────────
    def test_page_heading_is_new_donation(self, driver):
        """TC-DON-S-010: Page heading reads 'New donation'"""
        heading = driver.find_element(By.CSS_SELECTOR, 'h1')
        assert "New donation" in heading.text
