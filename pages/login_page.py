"""
Login Page Object Model — RescueBite
URL: /login
"""

from playwright.sync_api import Page

BASE_URL = "http://localhost:3000"


class LoginPage:
    """Page Object for the RescueBite login page."""

    EMAIL_INPUT    = 'input[type="email"]'
    PASSWORD_INPUT = 'input[type="password"]'
    SUBMIT_BUTTON  = 'button:has-text("Log in")'
    ERROR_MSG      = 'p.text-sm.text-clay'
    LOGO_LINK      = 'a[href="/"]'

    def __init__(self, page: Page):
        self.page = page
        self.url  = f"{BASE_URL}/login"

    def navigate(self):
        self.page.goto(self.url)

    def enter_email(self, email: str):
        self.page.fill(self.EMAIL_INPUT, email or "")

    def enter_password(self, password: str):
        self.page.fill(self.PASSWORD_INPUT, password or "")

    def click_login(self):
        self.page.click(self.SUBMIT_BUTTON)

    def press_enter(self):
        self.page.keyboard.press("Enter")

    def login(self, email: str, password: str):
        self.enter_email(email)
        self.enter_password(password)
        self.click_login()

    # ── Assertions helpers ──────────────────────────────────────────────────
    def get_error_message(self) -> str:
        locator = self.page.locator(self.ERROR_MSG)
        return locator.text_content() if locator.is_visible() else ""

    def is_error_visible(self) -> bool:
        return self.page.locator(self.ERROR_MSG).is_visible()

    def get_current_url(self) -> str:
        return self.page.url

    def is_password_masked(self) -> bool:
        return self.page.locator(self.PASSWORD_INPUT).get_attribute("type") == "password"

    def get_password_field_type(self) -> str:
        return self.page.locator(self.PASSWORD_INPUT).get_attribute("type")

    def is_submit_disabled(self) -> bool:
        return self.page.locator(self.SUBMIT_BUTTON).is_disabled()

    def get_submit_button_text(self) -> str:
        return self.page.locator(self.SUBMIT_BUTTON).text_content()
