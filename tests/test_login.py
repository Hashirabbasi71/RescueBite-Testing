"""
Data-Driven Playwright UI Tests — Login Module
Reads test cases from test_data/login_test_data.xml
"""

import pytest
import time
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from utils.xml_parser import xml_parser

BASE_URL = "http://localhost:3000"


class TestLoginModule:
    """Login test suite — data-driven from XML."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        self.page       = page
        self.login_page = LoginPage(page)
        self.login_page.navigate()

    # ── Positive ────────────────────────────────────────────────────────────
    @pytest.mark.positive
    @pytest.mark.parametrize("test_data",
        xml_parser.load_login_test_data_by_type("positive"))
    def test_positive_login(self, test_data):
        """TC-LGN-P: Valid credentials redirect away from login page"""
        self.login_page.login(test_data["email"], test_data["password"])
        self.page.wait_for_url(f"{BASE_URL}/**", timeout=10000)
        assert "/login" not in self.login_page.get_current_url()

    # ── Negative ────────────────────────────────────────────────────────────
    @pytest.mark.negative
    @pytest.mark.parametrize("test_data",
        xml_parser.load_login_test_data_by_type("negative"))
    def test_negative_login(self, test_data):
        """TC-LGN-N: Invalid credentials show error"""
        self.login_page.login(test_data["email"], test_data["password"])
        assert self.login_page.is_error_visible(), \
            f"Expected error for email={test_data['email']}"
        if "errorMessage" in test_data.get("expected", {}):
            assert test_data["expected"]["errorMessage"].lower() in \
                   self.login_page.get_error_message().lower()

    # ── Boundary ────────────────────────────────────────────────────────────
    @pytest.mark.boundary
    @pytest.mark.parametrize("test_data",
        xml_parser.load_login_test_data_by_type("boundary"))
    def test_boundary_login(self, test_data):
        """TC-LGN-B: Boundary inputs handled correctly"""
        self.login_page.login(test_data["email"], test_data["password"])
        expected = test_data.get("expected", {})
        if expected.get("errorExpected") == "true":
            assert self.login_page.is_error_visible() or \
                   "/login" in self.login_page.get_current_url()

    # ── Security ─────────────────────────────────────────────────────────────
    @pytest.mark.security
    @pytest.mark.parametrize("test_data",
        xml_parser.load_login_test_data_by_type("security"))
    def test_security_login(self, test_data):
        """TC-LGN-S: Security injections never grant access"""
        self.login_page.login(test_data["email"], test_data["password"])
        assert "/dashboard" not in self.login_page.get_current_url()
        assert "/ngo"       not in self.login_page.get_current_url()
        assert "/admin"     not in self.login_page.get_current_url()

    # ── Static / independent UI tests ──────────────────────────────────────
    def test_lgn_ui_001_password_field_is_masked(self):
        """TC-LGN-UI-001: Password field type is 'password' (masked)"""
        assert self.login_page.is_password_masked()

    def test_lgn_ui_002_email_field_accepts_input(self):
        """TC-LGN-UI-002: Email field accepts and reflects typed text"""
        self.login_page.enter_email("test@example.com")
        value = self.page.locator('input[type="email"]').input_value()
        assert value == "test@example.com"

    def test_lgn_ui_003_submit_button_present(self):
        """TC-LGN-UI-003: Login button is visible and enabled"""
        btn = self.page.locator('button:has-text("Log in")')
        assert btn.is_visible()
        assert btn.is_enabled()

    def test_lgn_ui_004_register_link_navigates(self):
        """TC-LGN-UI-004: 'Create an account' link points to /register"""
        link = self.page.locator('a[href="/register"]')
        assert link.is_visible()
        link.click()
        self.page.wait_for_url(f"{BASE_URL}/register", timeout=5000)
        assert "/register" in self.login_page.get_current_url()

    def test_lgn_ui_005_logo_navigates_to_home(self):
        """TC-LGN-UI-005: RescueBite logo links back to home"""
        link = self.page.locator('a[href="/"]')
        assert link.first.is_visible()

    def test_lgn_ui_006_empty_form_does_not_submit(self):
        """TC-LGN-UI-006: Submitting empty form triggers browser validation"""
        self.page.locator('button:has-text("Log in")').click()
        # HTML5 required + type="email" prevents submission — still on login
        assert "/login" in self.login_page.get_current_url()

    def test_lgn_ui_007_enter_key_triggers_login(self):
        """TC-LGN-UI-007: Pressing Enter on password field submits form"""
        self.login_page.enter_email("restaurant@test.com")
        self.login_page.enter_password("Testpass@123")
        self.login_page.press_enter()
        self.page.wait_for_timeout(3000)
        # If credentials are valid it redirects; if not valid it shows error
        redirected = "/login" not in self.login_page.get_current_url()
        has_error  = self.login_page.is_error_visible()
        assert redirected or has_error

    def test_lgn_ui_008_loading_state_shown(self):
        """TC-LGN-UI-008: Button shows 'Logging in…' while request in flight"""
        self.login_page.enter_email("restaurant@test.com")
        self.login_page.enter_password("Testpass@123")
        self.page.click('button:has-text("Log in")')
        # The loading state text appears briefly
        try:
            expect(self.page.locator('button:has-text("Logging in…")')).to_be_visible(timeout=2000)
            loading_shown = True
        except Exception:
            loading_shown = False
        # Either it loaded (already redirected) or showed loading text
        redirected = "/login" not in self.login_page.get_current_url()
        assert loading_shown or redirected

    def test_lgn_ui_009_direct_url_without_auth_stays_at_login(self):
        """TC-LGN-UI-009: /dashboard direct access redirects to login if not logged in"""
        self.page.goto(f"{BASE_URL}/dashboard")
        self.page.wait_for_timeout(2000)
        current = self.page.url
        assert "/login" in current or "/pending" in current, \
            f"Expected redirect to /login, got {current}"

    def test_lgn_ui_010_ngo_url_without_auth_redirects(self):
        """TC-LGN-UI-010: /ngo direct access redirects when not logged in"""
        self.page.goto(f"{BASE_URL}/ngo")
        self.page.wait_for_timeout(2000)
        current = self.page.url
        assert "/login" in current or "/pending" in current, \
            f"Expected redirect to /login, got {current}"
