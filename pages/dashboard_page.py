"""
Restaurant Dashboard Page Object Model — RescueBite
URL: /dashboard
"""

from playwright.sync_api import Page

BASE_URL = "http://localhost:3000"


class DashboardPage:
    """Page Object for the restaurant dashboard."""

    NEW_DONATION_BTN  = 'a[href="/dashboard/new"]'
    ACTIVE_SECTION    = 'section:has(h2:text("Active"))'
    HISTORY_SECTION   = 'section:has(div:text("History"))'
    STAT_CARDS        = '.stat-card'
    CANCEL_BUTTONS    = 'button:has-text("Cancel")'
    VERIFY_FORM       = 'form:has(input[placeholder])'  # 6-digit code form
    HEADING           = 'h1'

    def __init__(self, page: Page):
        self.page = page
        self.url  = f"{BASE_URL}/dashboard"

    def navigate(self):
        self.page.goto(self.url)

    def click_new_donation(self):
        self.page.click(self.NEW_DONATION_BTN)

    def get_stat_values(self) -> list:
        cards = self.page.locator(self.STAT_CARDS)
        return [cards.nth(i).locator('.font-display').text_content() for i in range(cards.count())]

    def count_active_listings(self) -> int:
        return self.page.locator('.card').count()

    def is_empty_state_visible(self) -> bool:
        return self.page.locator('text=No active donations yet').is_visible()

    def get_heading_text(self) -> str:
        return self.page.locator(self.HEADING).first.text_content()

    def get_current_url(self) -> str:
        return self.page.url
