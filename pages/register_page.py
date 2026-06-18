"""
Register Page Object Model — RescueBite
URL: /register
"""

from playwright.sync_api import Page

BASE_URL = "http://localhost:3000"


class RegisterPage:
    """Page Object for the RescueBite registration page."""

    RESTAURANT_ROLE_BTN = 'button:has-text("Restaurant")'
    NGO_ROLE_BTN        = 'button:has-text("NGO")'
    NAME_INPUT          = 'input:not([type="email"]):not([type="password"])'  # "Your name" — first text input
    EMAIL_INPUT         = 'input[type="email"]'
    PASSWORD_INPUT      = 'input[type="password"]'
    SUBMIT_BUTTON       = 'button:has-text("Create account")'
    ERROR_MSG           = 'p.text-sm.text-clay'
    LOGIN_LINK          = 'a[href="/login"]'

    def __init__(self, page: Page):
        self.page = page
        self.url  = f"{BASE_URL}/register"

    def navigate(self):
        self.page.goto(self.url)

    def select_role_restaurant(self):
        self.page.click(self.RESTAURANT_ROLE_BTN)

    def select_role_ngo(self):
        self.page.click(self.NGO_ROLE_BTN)

    def enter_name(self, name: str):
        self.page.fill(self.NAME_INPUT, name or "")

    def enter_email(self, email: str):
        self.page.fill(self.EMAIL_INPUT, email or "")

    def enter_password(self, password: str):
        self.page.fill(self.PASSWORD_INPUT, password or "")

    def click_create_account(self):
        self.page.click(self.SUBMIT_BUTTON)

    def register(self, role: str, name: str, email: str, password: str):
        if role == "NGO":
            self.select_role_ngo()
        else:
            self.select_role_restaurant()
        self.enter_name(name)
        self.enter_email(email)
        self.enter_password(password)
        self.click_create_account()

    # ── Assertion helpers ───────────────────────────────────────────────────
    def get_error_message(self) -> str:
        locator = self.page.locator(self.ERROR_MSG)
        return locator.text_content() if locator.is_visible() else ""

    def is_error_visible(self) -> bool:
        return self.page.locator(self.ERROR_MSG).is_visible()

    def get_current_url(self) -> str:
        return self.page.url

    def is_restaurant_role_active(self) -> bool:
        btn = self.page.locator(self.RESTAURANT_ROLE_BTN)
        return "border-rescue-500" in (btn.get_attribute("class") or "")

    def is_ngo_role_active(self) -> bool:
        btn = self.page.locator(self.NGO_ROLE_BTN)
        return "border-rescue-500" in (btn.get_attribute("class") or "")

    def get_submit_button_text(self) -> str:
        return self.page.locator(self.SUBMIT_BUTTON).text_content()
