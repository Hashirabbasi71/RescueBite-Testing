"""
Data-Driven Playwright UI Tests — Registration Module
Reads test cases from test_data/registration_test_data.xml
"""

import pytest
from playwright.sync_api import Page, expect
from pages.register_page import RegisterPage
from utils.xml_parser import xml_parser

BASE_URL = "https://rescuebite-sc83.vercel.app"


class TestRegistrationModule:
    """Registration test suite — data-driven from XML."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.page          = page
        self.register_page = RegisterPage(page)
        self.register_page.navigate()

    # ── Positive ────────────────────────────────────────────────────────────
    @pytest.mark.positive
    @pytest.mark.parametrize("test_data",
        xml_parser.load_registration_test_data_by_type("positive"))
    def test_positive_registration(self, test_data):
        """TC-REG-P: Valid inputs create account and redirect"""
        self.register_page.register(
            test_data["role"],
            test_data["name"],
            test_data["email"],
            test_data["password"],
        )
        self.page.wait_for_timeout(5000)
        current = self.register_page.get_current_url()
        assert "/register" not in current, \
            f"Still on /register — expected redirect. Error: {self.register_page.get_error_message()}"

    # ── Negative ────────────────────────────────────────────────────────────
    @pytest.mark.negative
    @pytest.mark.parametrize("test_data",
        xml_parser.load_registration_test_data_by_type("negative"))
    def test_negative_registration(self, test_data):
        """TC-REG-N: Invalid inputs show error or stay on /register"""
        self.register_page.register(
            test_data["role"],
            test_data["name"],
            test_data["email"],
            test_data["password"],
        )
        self.page.wait_for_timeout(3000)
        has_error = self.register_page.is_error_visible()
        still_on_page = "/register" in self.register_page.get_current_url()
        assert has_error or still_on_page

    # ── Boundary ────────────────────────────────────────────────────────────
    @pytest.mark.boundary
    @pytest.mark.parametrize("test_data",
        xml_parser.load_registration_test_data_by_type("boundary"))
    def test_boundary_registration(self, test_data):
        """TC-REG-B: Boundary inputs handled correctly"""
        self.register_page.register(
            test_data["role"],
            test_data["name"],
            test_data["email"],
            test_data["password"],
        )
        self.page.wait_for_timeout(3000)
        expected = test_data.get("expected", {})
        if expected.get("errorExpected") == "true":
            assert self.register_page.is_error_visible() or \
                   "/register" in self.register_page.get_current_url()

    # ── Static / independent UI tests ──────────────────────────────────────
    def test_reg_ui_001_restaurant_role_selected_by_default(self):
        """TC-REG-UI-001: Restaurant role is selected by default"""
        assert self.register_page.is_restaurant_role_active()

    def test_reg_ui_002_switch_to_ngo_role(self):
        """TC-REG-UI-002: Clicking NGO button activates NGO role"""
        self.register_page.select_role_ngo()
        assert self.register_page.is_ngo_role_active()
        assert not self.register_page.is_restaurant_role_active()

    def test_reg_ui_003_switch_back_to_restaurant(self):
        """TC-REG-UI-003: Clicking Restaurant button re-activates restaurant role"""
        self.register_page.select_role_ngo()
        self.register_page.select_role_restaurant()
        assert self.register_page.is_restaurant_role_active()
        assert not self.register_page.is_ngo_role_active()

    def test_reg_ui_004_password_field_is_masked(self):
        """TC-REG-UI-004: Password field is masked"""
        field_type = self.page.locator('input[type="password"]').get_attribute("type")
        assert field_type == "password"

    def test_reg_ui_005_login_link_navigates(self):
        """TC-REG-UI-005: 'Log in' link navigates to /login"""
        link = self.page.locator('a[href="/login"]')
        assert link.is_visible()
        link.click()
        self.page.wait_for_url(f"{BASE_URL}/login", timeout=5000)
        assert "/login" in self.page.url

    def test_reg_ui_006_submit_button_visible(self):
        """TC-REG-UI-006: Create account button is visible"""
        btn = self.page.locator('button:has-text("Create account")')
        assert btn.is_visible()

    def test_reg_ui_007_short_password_shows_error(self):
        """TC-REG-UI-007: Password shorter than 6 characters produces error"""
        self.register_page.select_role_restaurant()
        self.register_page.enter_name("Test User")
        self.register_page.enter_email("shortpass@test.com")
        self.register_page.enter_password("abc")
        self.register_page.click_create_account()
        self.page.wait_for_timeout(3000)
        has_error = self.register_page.is_error_visible()
        still_on = "/register" in self.register_page.get_current_url()
        assert has_error or still_on

    def test_reg_ui_008_invalid_email_format_blocked(self):
        """TC-REG-UI-008: Invalid email format blocked by HTML5 validation"""
        self.register_page.enter_name("Test User")
        self.register_page.enter_email("not-an-email")
        self.register_page.enter_password("validpass123")
        self.register_page.click_create_account()
        # HTML5 type="email" prevents submission
        assert "/register" in self.register_page.get_current_url()

    def test_reg_ui_009_logo_navigates_to_home(self):
        """TC-REG-UI-009: RescueBite logo links to home page"""
        link = self.page.locator('a[href="/"]')
        assert link.first.is_visible()

    def test_reg_ui_010_both_role_buttons_visible(self):
        """TC-REG-UI-010: Both role selector buttons are visible"""
        assert self.page.locator('button:has-text("Restaurant")').is_visible()
        assert self.page.locator('button:has-text("NGO")').is_visible()
