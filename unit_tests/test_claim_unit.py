"""
UNIT TESTS — NGO Claim & Collection Code Module (15 tests)
Covers claim eligibility, collection code format, status transitions,
and NGO receipt confirmation logic.
"""

import pytest
import re
from datetime import datetime, timedelta


# ── Mock business-logic functions ──────────────────────────────────────────────

VALID_STATUSES = {"AVAILABLE", "CLAIMED", "COLLECTED", "EXPIRED", "CANCELLED"}


def can_ngo_claim(listing_status: str, pickup_end: datetime) -> tuple:
    if listing_status != "AVAILABLE":
        return False, f"Listing is not available (status: {listing_status})"
    if pickup_end < datetime.now():
        return False, "Listing has expired"
    return True, ""


def validate_collection_code(code: str) -> tuple:
    """Collection codes are exactly 6 uppercase alphanumeric characters."""
    if not code or len(code.strip()) == 0:
        return False, "Collection code is required"
    if not re.fullmatch(r'[A-Z0-9]{6}', code.strip()):
        return False, "Collection code must be 6 uppercase alphanumeric characters"
    return True, ""


def transition_status(current: str, action: str) -> tuple:
    """
    Allowed transitions:
      AVAILABLE → CLAIMED   (NGO claims)
      AVAILABLE → CANCELLED (restaurant cancels)
      CLAIMED   → COLLECTED (restaurant verifies code)
      AVAILABLE → EXPIRED   (system sets after pickup_end)
    """
    TRANSITIONS = {
        ("AVAILABLE", "claim"):   "CLAIMED",
        ("AVAILABLE", "cancel"):  "CANCELLED",
        ("AVAILABLE", "expire"):  "EXPIRED",
        ("CLAIMED",   "collect"): "COLLECTED",
    }
    new_status = TRANSITIONS.get((current, action))
    if new_status is None:
        return None, f"Invalid transition: {current} + {action}"
    return new_status, ""


def calculate_metrics(listings: list) -> dict:
    """Calculate dashboard metrics from a list of listing dicts."""
    active    = [l for l in listings if l["status"] in ("AVAILABLE", "CLAIMED")]
    collected = [l for l in listings if l["status"] == "COLLECTED"]
    total_qty = sum(l["quantity"] for l in listings)
    return {
        "active":     len(active),
        "collected":  len(collected),
        "total_bags": total_qty,
    }


def ngo_can_confirm_receipt(listing: dict, ngo_id: str) -> tuple:
    if listing["status"] != "COLLECTED":
        return False, "Listing has not been collected yet"
    if listing["claimed_by_id"] != ngo_id:
        return False, "You did not claim this listing"
    if listing.get("ngo_confirmed"):
        return False, "Receipt already confirmed"
    return True, ""


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestClaimEligibility:
    """UNT-CLM-001 to 004"""

    def test_01_available_listing_can_be_claimed(self):
        """UNT-CLM-001: AVAILABLE listing with future pickup can be claimed"""
        ok, _ = can_ngo_claim("AVAILABLE", datetime.now() + timedelta(hours=2))
        assert ok is True

    def test_02_claimed_listing_cannot_be_reclaimed(self):
        """UNT-CLM-002: Already CLAIMED listing cannot be claimed again"""
        ok, error = can_ngo_claim("CLAIMED", datetime.now() + timedelta(hours=2))
        assert ok is False
        assert "available" in error.lower()

    def test_03_expired_listing_cannot_be_claimed(self):
        """UNT-CLM-003: Listing past pickup_end cannot be claimed"""
        ok, error = can_ngo_claim("AVAILABLE", datetime.now() - timedelta(hours=1))
        assert ok is False
        assert "expired" in error.lower()

    def test_04_collected_listing_cannot_be_claimed(self):
        """UNT-CLM-004: COLLECTED listing cannot be claimed"""
        ok, error = can_ngo_claim("COLLECTED", datetime.now() + timedelta(hours=1))
        assert ok is False
        assert "available" in error.lower()


class TestCollectionCodeValidation:
    """UNT-CLM-005 to 008"""

    def test_05_valid_6_char_code_passes(self):
        """UNT-CLM-005: Valid 6-char uppercase alphanumeric code passes"""
        is_valid, _ = validate_collection_code("A1B2C3")
        assert is_valid is True

    def test_06_code_too_short_fails(self):
        """UNT-CLM-006: 5-character code fails"""
        is_valid, error = validate_collection_code("AB123")
        assert is_valid is False
        assert "6" in error

    def test_07_code_with_lowercase_fails(self):
        """UNT-CLM-007: Lowercase characters in code fail"""
        is_valid, error = validate_collection_code("ab1234")
        assert is_valid is False

    def test_08_empty_code_fails(self):
        """UNT-CLM-008: Empty code fails with required message"""
        is_valid, error = validate_collection_code("")
        assert is_valid is False
        assert "required" in error.lower()


class TestStatusTransitions:
    """UNT-CLM-009 to 012"""

    def test_09_available_to_claimed(self):
        """UNT-CLM-009: AVAILABLE + claim → CLAIMED"""
        new_status, _ = transition_status("AVAILABLE", "claim")
        assert new_status == "CLAIMED"

    def test_10_available_to_cancelled(self):
        """UNT-CLM-010: AVAILABLE + cancel → CANCELLED"""
        new_status, _ = transition_status("AVAILABLE", "cancel")
        assert new_status == "CANCELLED"

    def test_11_claimed_to_collected(self):
        """UNT-CLM-011: CLAIMED + collect → COLLECTED"""
        new_status, _ = transition_status("CLAIMED", "collect")
        assert new_status == "COLLECTED"

    def test_12_invalid_transition_returns_error(self):
        """UNT-CLM-012: COLLECTED + claim is invalid"""
        new_status, error = transition_status("COLLECTED", "claim")
        assert new_status is None
        assert "invalid" in error.lower()


class TestDashboardMetrics:
    """UNT-CLM-013"""

    def test_13_metrics_calculated_correctly(self):
        """UNT-CLM-013: Metrics count active, collected, and total bags"""
        listings = [
            {"status": "AVAILABLE",  "quantity": 5},
            {"status": "CLAIMED",    "quantity": 3},
            {"status": "COLLECTED",  "quantity": 8},
            {"status": "EXPIRED",    "quantity": 2},
            {"status": "CANCELLED",  "quantity": 1},
        ]
        metrics = calculate_metrics(listings)
        assert metrics["active"]     == 2   # AVAILABLE + CLAIMED
        assert metrics["collected"]  == 1
        assert metrics["total_bags"] == 19


class TestNgoReceiptConfirmation:
    """UNT-CLM-014 to 015"""

    def test_14_eligible_ngo_can_confirm_receipt(self):
        """UNT-CLM-014: NGO that claimed a COLLECTED listing can confirm receipt"""
        listing = {"status": "COLLECTED", "claimed_by_id": "ngo-1", "ngo_confirmed": False}
        ok, _ = ngo_can_confirm_receipt(listing, "ngo-1")
        assert ok is True

    def test_15_cannot_double_confirm_receipt(self):
        """UNT-CLM-015: Already confirmed receipt returns error"""
        listing = {"status": "COLLECTED", "claimed_by_id": "ngo-1", "ngo_confirmed": True}
        ok, error = ngo_can_confirm_receipt(listing, "ngo-1")
        assert ok is False
        assert "already" in error.lower()
