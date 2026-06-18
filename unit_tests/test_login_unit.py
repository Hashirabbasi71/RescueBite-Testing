"""
UNIT TESTS — Login Module Business Logic (15 tests)
Tests email/password validation and authentication logic mirroring
what the RescueBite Next.js login page enforces.
"""

import pytest
import re


# ── Mock business-logic functions ──────────────────────────────────────────────

def validate_email(email: str) -> tuple:
    """Validate email format (HTML5 email rules)."""
    if not email or len(email.strip()) == 0:
        return False, "Email is required"
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(pattern, email.strip()):
        return False, "Invalid email format"
    if len(email) > 254:
        return False, "Email exceeds maximum length"
    return True, ""


def validate_password(password: str) -> tuple:
    """Validate password (Supabase requires min 6 characters)."""
    if not password or len(password.strip()) == 0:
        return False, "Password is required"
    if len(password) < 6:
        return False, "Password should be at least 6 characters"
    return True, ""


def authenticate_user(email: str, password: str) -> tuple:
    """Simulate Supabase signInWithPassword responses."""
    VALID_USERS = {
        "restaurant@test.com": "Testpass@123",
        "ngo@test.com":        "Testpass@123",
        "admin@rescuebite.com": "adminpass123",
    }
    if email not in VALID_USERS:
        return False, "Invalid login credentials"
    if VALID_USERS[email] != password:
        return False, "Invalid login credentials"
    return True, "Login successful"


def sanitize_email_input(email: str) -> str:
    """Strip whitespace from email before sending to Supabase (mirrors .trim())."""
    if not email:
        return ""
    return email.strip()


def get_redirect_path_after_login(role: str) -> str:
    """Determine post-login redirect based on user role."""
    role_map = {
        "RESTAURANT": "/dashboard",
        "NGO":        "/ngo",
        "ADMIN":      "/admin",
    }
    return role_map.get(role, "/go")


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestEmailValidation:
    """UNT-LGN-001 to 005 — email field validation"""

    def test_01_valid_email_passes(self):
        """UNT-LGN-001: Valid email passes validation"""
        is_valid, _ = validate_email("restaurant@test.com")
        assert is_valid is True

    def test_02_empty_email_fails(self):
        """UNT-LGN-002: Empty email fails with required message"""
        is_valid, error = validate_email("")
        assert is_valid is False
        assert "required" in error.lower()

    def test_03_missing_at_symbol_fails(self):
        """UNT-LGN-003: Email without @ symbol fails format check"""
        is_valid, error = validate_email("notanemail.com")
        assert is_valid is False
        assert "format" in error.lower()

    def test_04_missing_domain_fails(self):
        """UNT-LGN-004: Email without domain fails format check"""
        is_valid, error = validate_email("user@")
        assert is_valid is False
        assert "format" in error.lower()

    def test_05_email_too_long_fails(self):
        """UNT-LGN-005: Email > 254 chars fails"""
        long_email = "a" * 250 + "@b.com"
        is_valid, error = validate_email(long_email)
        assert is_valid is False
        assert "maximum" in error.lower()


class TestPasswordValidation:
    """UNT-LGN-006 to 009 — password field validation"""

    def test_06_valid_password_passes(self):
        """UNT-LGN-006: Valid password (>= 6 chars) passes"""
        is_valid, _ = validate_password("Testpass@123")
        assert is_valid is True

    def test_07_empty_password_fails(self):
        """UNT-LGN-007: Empty password fails with required message"""
        is_valid, error = validate_password("")
        assert is_valid is False
        assert "required" in error.lower()

    def test_08_password_too_short_fails(self):
        """UNT-LGN-008: Password < 6 chars fails with length message"""
        is_valid, error = validate_password("abc")
        assert is_valid is False
        assert "6" in error

    def test_09_password_exactly_6_chars_passes(self):
        """UNT-LGN-009: Password of exactly 6 characters passes (boundary)"""
        is_valid, _ = validate_password("abcdef")
        assert is_valid is True


class TestAuthentication:
    """UNT-LGN-010 to 013 — credential verification"""

    def test_10_valid_credentials_succeed(self):
        """UNT-LGN-010: Valid restaurant credentials authenticate"""
        success, _ = authenticate_user("restaurant@test.com", "Testpass@123")
        assert success is True

    def test_11_wrong_password_fails(self):
        """UNT-LGN-011: Wrong password returns error"""
        success, message = authenticate_user("restaurant@test.com", "wrongpassword")
        assert success is False
        assert "credentials" in message.lower()

    def test_12_unknown_email_fails(self):
        """UNT-LGN-012: Unknown email returns error"""
        success, message = authenticate_user("unknown@nobody.com", "Testpass@123")
        assert success is False
        assert "credentials" in message.lower()

    def test_13_ngo_credentials_succeed(self):
        """UNT-LGN-013: Valid NGO credentials authenticate"""
        success, _ = authenticate_user("ngo@test.com", "Testpass@123")
        assert success is True


class TestEmailSanitization:
    """UNT-LGN-014 to 015 — whitespace trimming"""

    def test_14_leading_trailing_spaces_trimmed(self):
        """UNT-LGN-014: Leading/trailing spaces are removed from email"""
        result = sanitize_email_input("  restaurant@test.com  ")
        assert result == "restaurant@test.com"

    def test_15_empty_string_returns_empty(self):
        """UNT-LGN-015: Empty string returns empty after sanitization"""
        result = sanitize_email_input("")
        assert result == ""


class TestRedirectLogic:
    """UNT-LGN-016 to 018 — post-login routing"""

    def test_16_restaurant_redirects_to_dashboard(self):
        """UNT-LGN-016: RESTAURANT role redirects to /dashboard"""
        path = get_redirect_path_after_login("RESTAURANT")
        assert path == "/dashboard"

    def test_17_ngo_redirects_to_ngo(self):
        """UNT-LGN-017: NGO role redirects to /ngo"""
        path = get_redirect_path_after_login("NGO")
        assert path == "/ngo"

    def test_18_admin_redirects_to_admin(self):
        """UNT-LGN-018: ADMIN role redirects to /admin"""
        path = get_redirect_path_after_login("ADMIN")
        assert path == "/admin"
