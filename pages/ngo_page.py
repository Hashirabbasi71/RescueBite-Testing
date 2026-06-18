"""
NGO Pages Object Model — RescueBite
Covers: /ngo (discover), /ngo/claims
"""

from playwright.sync_api import Page

BASE_URL = "https://rescuebite-sc83.vercel.app"


class NgoDiscoverPage:
    """Page Object for the NGO food discovery page."""

    HEADING          = 'h1'
    STAT_CARDS       = '.stat-card'
    LISTING_CARDS    = '.card'
    CLAIM_BUTTONS    = 'button:has-text("Claim")'
    MAP_CONTAINER    = '.leaflet-container'

    def __init__(self, page: Page):
        self.page = page
        self.url  = f"{BASE_URL}/ngo"

    def navigate(self):
        self.page.goto(self.url)

    def get_heading_text(self) -> str:
        return self.page.locator(self.HEADING).first.text_content()

    def count_listings(self) -> int:
        return self.page.locator(self.LISTING_CARDS).count()

    def count_claim_buttons(self) -> int:
        return self.page.locator(self.CLAIM_BUTTONS).count()

    def is_map_visible(self) -> bool:
        return self.page.locator(self.MAP_CONTAINER).is_visible()

    def get_current_url(self) -> str:
        return self.page.url


class NgoClaimsPage:
    """Page Object for the NGO claims management page."""

    HEADING             = 'h1'
    STAT_CARDS          = '.stat-card'
    CLAIM_CARDS         = '.card'
    DIRECTIONS_LINKS    = 'a:has-text("Directions")'
    COLLECTION_CODE     = '.font-display.tracking-\\[0\\.3em\\]'
    CONFIRM_RECEIPT_BTN = 'button:has-text("Confirm receipt")'
    EMPTY_STATE         = 'text=You haven\'t claimed any donations yet'

    def __init__(self, page: Page):
        self.page = page
        self.url  = f"{BASE_URL}/ngo/claims"

    def navigate(self):
        self.page.goto(self.url)

    def get_heading_text(self) -> str:
        return self.page.locator(self.HEADING).first.text_content()

    def count_claim_cards(self) -> int:
        return self.page.locator(self.CLAIM_CARDS).count()

    def is_empty_state_visible(self) -> bool:
        return self.page.locator(self.EMPTY_STATE).is_visible()

    def get_collection_codes(self) -> list:
        codes = self.page.locator(self.COLLECTION_CODE)
        return [codes.nth(i).text_content() for i in range(codes.count())]

    def count_directions_links(self) -> int:
        return self.page.locator(self.DIRECTIONS_LINKS).count()

    def get_current_url(self) -> str:
        return self.page.url
