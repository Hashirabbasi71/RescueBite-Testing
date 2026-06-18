"""
New Donation Page Object Model — RescueBite
URL: /dashboard/new
"""

from playwright.sync_api import Page

BASE_URL = "https://rescuebite-sc83.vercel.app"


class NewDonationPage:
    """Page Object for the new donation form."""

    TITLE_INPUT        = 'input[placeholder="e.g. Mixed dinner surprise bag"]'
    DESCRIPTION_INPUT  = 'textarea'
    CATEGORY_SELECT    = 'select'
    QUANTITY_INPUT     = 'input[type="number"]'
    PICKUP_DATETIME_INPUT = 'input[type="datetime-local"]'
    IMAGE_INPUT        = 'input[type="file"]'
    SUBMIT_BUTTON      = 'button:has-text("Post donation")'
    ERROR_MSG          = 'p.text-sm.text-clay'
    REMOVE_IMAGE_BTN   = 'button:has(svg):near(img[alt="Preview"])'

    def __init__(self, page: Page):
        self.page = page
        self.url  = f"{BASE_URL}/dashboard/new"

    def navigate(self):
        self.page.goto(self.url)

    def enter_title(self, title: str):
        self.page.fill(self.TITLE_INPUT, title or "")

    def enter_description(self, description: str):
        self.page.fill(self.DESCRIPTION_INPUT, description or "")

    def select_category(self, category: str):
        self.page.select_option(self.CATEGORY_SELECT, category)

    def enter_quantity(self, quantity: int):
        self.page.fill(self.QUANTITY_INPUT, str(quantity))

    def set_pickup_start(self, datetime_local: str):
        self.page.locator(self.PICKUP_DATETIME_INPUT).nth(0).fill(datetime_local)

    def set_pickup_end(self, datetime_local: str):
        self.page.locator(self.PICKUP_DATETIME_INPUT).nth(1).fill(datetime_local)

    def click_submit(self):
        self.page.click(self.SUBMIT_BUTTON)

    def fill_form(self, title: str, category: str, quantity: int,
                  pickup_start: str, pickup_end: str, description: str = ""):
        self.enter_title(title)
        if description:
            self.enter_description(description)
        self.select_category(category)
        self.enter_quantity(quantity)
        self.set_pickup_start(pickup_start)
        self.set_pickup_end(pickup_end)

    # ── Assertion helpers ───────────────────────────────────────────────────
    def get_error_message(self) -> str:
        locator = self.page.locator(self.ERROR_MSG)
        return locator.text_content() if locator.is_visible() else ""

    def is_error_visible(self) -> bool:
        return self.page.locator(self.ERROR_MSG).is_visible()

    def get_submit_button_text(self) -> str:
        return self.page.locator(self.SUBMIT_BUTTON).text_content()

    def get_current_url(self) -> str:
        return self.page.url

    def is_image_preview_visible(self) -> bool:
        return self.page.locator('img[alt="Preview"]').is_visible()
