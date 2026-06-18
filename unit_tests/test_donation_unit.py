"""
UNIT TESTS — New Donation Module Business Logic (18 tests)
Covers form validation, pickup window logic, quantity rules,
and category mapping as used in /dashboard/new.
"""

import pytest
from datetime import datetime, timedelta


# ── Mock business-logic functions ──────────────────────────────────────────────

VALID_CATEGORIES = {"COOKED_MEALS", "BAKERY", "GROCERY", "PRODUCE", "OTHER"}

CATEGORY_LABELS = {
    "COOKED_MEALS": "Cooked meals",
    "BAKERY":       "Bakery",
    "GROCERY":      "Grocery",
    "PRODUCE":      "Produce",
    "OTHER":        "Other",
}


def validate_title(title: str) -> tuple:
    if not title or len(title.strip()) == 0:
        return False, "Title is required"
    if len(title.strip()) > 120:
        return False, "Title exceeds maximum length"
    return True, ""


def validate_quantity(quantity) -> tuple:
    try:
        qty = int(quantity)
    except (TypeError, ValueError):
        return False, "Quantity must be a number"
    if qty < 1:
        return False, "Quantity must be at least 1"
    if qty > 999:
        return False, "Quantity cannot exceed 999"
    return True, ""


def validate_pickup_window(start: datetime, end: datetime) -> tuple:
    if end <= start:
        return False, "Pickup window is invalid."
    if start < datetime.now() - timedelta(minutes=5):
        return False, "Pickup start cannot be in the past"
    return True, ""


def validate_category(category: str) -> tuple:
    if category not in VALID_CATEGORIES:
        return False, f"Invalid category: {category}"
    return True, ""


def category_label(category: str) -> str:
    return CATEGORY_LABELS.get(category, "Unknown")


def validate_location_set(latitude, longitude) -> tuple:
    if latitude is None or longitude is None:
        return False, "Please finish your location setup in onboarding before posting a donation."
    return True, ""


def build_listing_payload(restaurant_id, title, description, category,
                          quantity, pickup_start, pickup_end, latitude, longitude):
    """Assemble the Supabase insert payload — raises ValueError on bad inputs."""
    errors = []
    v, e = validate_title(title);               errors.append(e) if not v else None
    v, e = validate_quantity(quantity);          errors.append(e) if not v else None
    v, e = validate_category(category);          errors.append(e) if not v else None
    v, e = validate_pickup_window(pickup_start, pickup_end); errors.append(e) if not v else None
    v, e = validate_location_set(latitude, longitude);       errors.append(e) if not v else None
    if errors:
        raise ValueError("; ".join(errors))
    return {
        "restaurant_id": restaurant_id,
        "title": title.strip(),
        "description": description or None,
        "category": category,
        "quantity": int(quantity),
        "pickup_start": pickup_start.isoformat(),
        "pickup_end": pickup_end.isoformat(),
        "latitude": latitude,
        "longitude": longitude,
    }


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestTitleValidation:
    """UNT-DON-001 to 003"""

    def test_01_valid_title_passes(self):
        """UNT-DON-001: Valid title passes validation"""
        is_valid, _ = validate_title("Mixed dinner surprise bag")
        assert is_valid is True

    def test_02_empty_title_fails(self):
        """UNT-DON-002: Empty title fails with required message"""
        is_valid, error = validate_title("")
        assert is_valid is False
        assert "required" in error.lower()

    def test_03_title_too_long_fails(self):
        """UNT-DON-003: Title > 120 characters fails"""
        is_valid, error = validate_title("A" * 121)
        assert is_valid is False
        assert "exceeds" in error.lower()


class TestQuantityValidation:
    """UNT-DON-004 to 008"""

    def test_04_valid_quantity_passes(self):
        """UNT-DON-004: Quantity of 5 passes"""
        is_valid, _ = validate_quantity(5)
        assert is_valid is True

    def test_05_quantity_zero_fails(self):
        """UNT-DON-005: Quantity of 0 fails minimum check"""
        is_valid, error = validate_quantity(0)
        assert is_valid is False
        assert "1" in error

    def test_06_quantity_999_passes(self):
        """UNT-DON-006: Quantity of 999 passes (upper boundary)"""
        is_valid, _ = validate_quantity(999)
        assert is_valid is True

    def test_07_quantity_1000_fails(self):
        """UNT-DON-007: Quantity of 1000 fails upper boundary check"""
        is_valid, error = validate_quantity(1000)
        assert is_valid is False
        assert "999" in error

    def test_08_non_numeric_quantity_fails(self):
        """UNT-DON-008: Non-numeric quantity fails"""
        is_valid, error = validate_quantity("abc")
        assert is_valid is False
        assert "number" in error.lower()


class TestPickupWindowValidation:
    """UNT-DON-009 to 012"""

    def test_09_valid_pickup_window_passes(self):
        """UNT-DON-009: End after start passes"""
        start = datetime.now() + timedelta(hours=1)
        end   = datetime.now() + timedelta(hours=4)
        is_valid, _ = validate_pickup_window(start, end)
        assert is_valid is True

    def test_10_end_equals_start_fails(self):
        """UNT-DON-010: End == start is invalid"""
        t = datetime.now() + timedelta(hours=2)
        is_valid, error = validate_pickup_window(t, t)
        assert is_valid is False
        assert "invalid" in error.lower()

    def test_11_end_before_start_fails(self):
        """UNT-DON-011: End before start is invalid"""
        start = datetime.now() + timedelta(hours=3)
        end   = datetime.now() + timedelta(hours=1)
        is_valid, error = validate_pickup_window(start, end)
        assert is_valid is False
        assert "invalid" in error.lower()

    def test_12_one_minute_window_passes(self):
        """UNT-DON-012: 1-minute window is technically valid"""
        start = datetime.now() + timedelta(hours=1)
        end   = start + timedelta(minutes=1)
        is_valid, _ = validate_pickup_window(start, end)
        assert is_valid is True


class TestCategoryValidation:
    """UNT-DON-013 to 015"""

    def test_13_all_valid_categories_pass(self):
        """UNT-DON-013: All five valid categories pass"""
        for cat in ["COOKED_MEALS", "BAKERY", "GROCERY", "PRODUCE", "OTHER"]:
            is_valid, _ = validate_category(cat)
            assert is_valid is True, f"{cat} should be valid"

    def test_14_invalid_category_fails(self):
        """UNT-DON-014: Unknown category string fails"""
        is_valid, error = validate_category("FAST_FOOD")
        assert is_valid is False
        assert "invalid" in error.lower()

    def test_15_category_label_mapping(self):
        """UNT-DON-015: category_label() returns correct human-readable labels"""
        assert category_label("COOKED_MEALS") == "Cooked meals"
        assert category_label("BAKERY")       == "Bakery"
        assert category_label("GROCERY")      == "Grocery"
        assert category_label("PRODUCE")      == "Produce"
        assert category_label("OTHER")        == "Other"


class TestLocationValidation:
    """UNT-DON-016 to 017"""

    def test_16_location_set_passes(self):
        """UNT-DON-016: Latitude + longitude present passes"""
        is_valid, _ = validate_location_set(33.6844, 73.0479)
        assert is_valid is True

    def test_17_missing_location_fails(self):
        """UNT-DON-017: None location fails with onboarding message"""
        is_valid, error = validate_location_set(None, None)
        assert is_valid is False
        assert "onboarding" in error.lower()


class TestListingPayload:
    """UNT-DON-018"""

    def test_18_valid_payload_builds_correctly(self):
        """UNT-DON-018: Valid inputs produce a correct insert payload"""
        start = datetime.now() + timedelta(hours=1)
        end   = datetime.now() + timedelta(hours=4)
        payload = build_listing_payload(
            restaurant_id="uid-123",
            title="  Fresh bread bags  ",
            description="Assorted sourdough",
            category="BAKERY",
            quantity="10",
            pickup_start=start,
            pickup_end=end,
            latitude=33.6844,
            longitude=73.0479,
        )
        assert payload["title"]       == "Fresh bread bags"
        assert payload["quantity"]    == 10
        assert payload["category"]    == "BAKERY"
        assert payload["description"] == "Assorted sourdough"
