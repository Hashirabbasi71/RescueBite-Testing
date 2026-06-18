"""
Data-Driven Playwright UI Tests — New Donation Module
Reads test cases from test_data/donation_test_data.xml
Requires a logged-in restaurant session (restaurant_page fixture from conftest.py).
"""

import pytest
from playwright.sync_api import Page, expect
from pages.new_donation_page import NewDonationPage
from utils.xml_parser import xml_parser

BASE_URL = "http://localhost:3000"


class TestNewDonationModule:
    """New donation test suite — data-driven from XML."""

    @pytest.fixture(autouse=True)
    def setup(self, restaurant_page: Page):
        """Uses logged-in restaurant session."""
        self.page          = restaurant_page
        self.donation_page = NewDonationPage(restaurant_page)
        self.donation_page.navigate()

    # ── Positive ────────────────────────────────────────────────────────────
    @pytest.mark.positive
    @pytest.mark.parametrize("test_data",
        xml_parser.load_donation_test_data_by_type("positive"))
    def test_positive_donation(self, test_data):
        """TC-DON-P: Valid donation form submits and redirects to dashboard"""
        self.donation_page.fill_form(
            title        = test_data["title"],
            category     = test_data["category"],
            quantity     = int(test_data["quantity"]),
            pickup_start = test_data["pickupStart"],
            pickup_end   = test_data["pickupEnd"],
            description  = test_data.get("description", ""),
        )
        self.donation_page.click_submit()
        self.page.wait_for_timeout(5000)
        current = self.donation_page.get_current_url()
        assert "/dashboard" in current, \
            f"Expected /dashboard after submit. Error: {self.donation_page.get_error_message()}"

    # ── Negative ────────────────────────────────────────────────────────────
    @pytest.mark.negative
    @pytest.mark.parametrize("test_data",
        xml_parser.load_donation_test_data_by_type("negative"))
    def test_negative_donation(self, test_data):
        """TC-DON-N: Invalid form inputs show error message"""
        self.donation_page.fill_form(
            title        = test_data["title"],
            category     = test_data["category"],
            quantity     = int(test_data.get("quantity", 1)),
            pickup_start = test_data["pickupStart"],
            pickup_end   = test_data["pickupEnd"],
        )
        self.donation_page.click_submit()
        self.page.wait_for_timeout(3000)
        assert self.donation_page.is_error_visible() or \
               "/dashboard/new" in self.donation_page.get_current_url()

    # ── Boundary ────────────────────────────────────────────────────────────
    @pytest.mark.boundary
    @pytest.mark.parametrize("test_data",
        xml_parser.load_donation_test_data_by_type("boundary"))
    def test_boundary_donation(self, test_data):
        """TC-DON-B: Boundary values handled by the form"""
        self.donation_page.fill_form(
            title        = test_data["title"],
            category     = test_data["category"],
            quantity     = int(test_data.get("quantity", 1)),
            pickup_start = test_data["pickupStart"],
            pickup_end   = test_data["pickupEnd"],
        )
        self.donation_page.click_submit()
        self.page.wait_for_timeout(3000)
        expected = test_data.get("expected", {})
        if expected.get("errorExpected") == "true":
            assert self.donation_page.is_error_visible() or \
                   "/dashboard/new" in self.donation_page.get_current_url()

    # ── Static / independent UI tests ──────────────────────────────────────
    def test_don_ui_001_form_title_input_present(self):
        """TC-DON-UI-001: Title input field is visible"""
        assert self.page.locator('input[placeholder="e.g. Mixed dinner surprise bag"]').is_visible()

    def test_don_ui_002_category_dropdown_has_five_options(self):
        """TC-DON-UI-002: Category dropdown contains all 5 options"""
        options = self.page.locator('select option')
        assert options.count() == 5

    def test_don_ui_003_quantity_min_is_1(self):
        """TC-DON-UI-003: Quantity input has min attribute of 1"""
        qty_input = self.page.locator('input[type="number"]')
        assert qty_input.get_attribute("min") == "1"

    def test_don_ui_004_quantity_max_is_999(self):
        """TC-DON-UI-004: Quantity input has max attribute of 999"""
        qty_input = self.page.locator('input[type="number"]')
        assert qty_input.get_attribute("max") == "999"

    def test_don_ui_005_two_datetime_inputs_present(self):
        """TC-DON-UI-005: Two datetime-local inputs exist for pickup window"""
        inputs = self.page.locator('input[type="datetime-local"]')
        assert inputs.count() == 2

    def test_don_ui_006_image_upload_area_visible(self):
        """TC-DON-UI-006: Image upload area is visible"""
        upload_label = self.page.locator('text=Click to upload a photo of the food')
        assert upload_label.is_visible()

    def test_don_ui_007_submit_button_text(self):
        """TC-DON-UI-007: Submit button reads 'Post donation'"""
        btn_text = self.donation_page.get_submit_button_text()
        assert "Post donation" in btn_text

    def test_don_ui_008_empty_title_blocked_by_html5(self):
        """TC-DON-UI-008: Required title field prevents submission when empty"""
        # Leave title empty, fill rest minimally
        self.page.click('button:has-text("Post donation")')
        # HTML5 required prevents navigation
        assert "/dashboard/new" in self.donation_page.get_current_url()

    def test_don_ui_009_default_quantity_is_1(self):
        """TC-DON-UI-009: Default quantity value is 1"""
        default_qty = self.page.locator('input[type="number"]').input_value()
        assert default_qty == "1"

    def test_don_ui_010_description_field_optional(self):
        """TC-DON-UI-010: Description textarea has no required attribute"""
        textarea = self.page.locator('textarea')
        assert textarea.get_attribute("required") is None
