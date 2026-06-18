"""
XML Parser Utility — RescueBite Testing Project
Reads test data from test_data/*.xml files and returns structured dicts.
"""

import xml.etree.ElementTree as ET
import os
from typing import List, Dict, Any


class XMLTestDataParser:
    """Parser for all RescueBite XML test data files."""

    def __init__(self, data_dir: str = "test_data"):
        self.data_dir = data_dir

    # ── Internal helpers ────────────────────────────────────────────────────

    def _parse_file(self, filename: str) -> ET.Element:
        path = os.path.join(self.data_dir, filename)
        tree = ET.parse(path)
        return tree.getroot()

    @staticmethod
    def _text(element: ET.Element, tag: str) -> str:
        child = element.find(tag)
        return (child.text or "") if child is not None else ""

    @staticmethod
    def _build_expected(test_case: ET.Element) -> Dict[str, str]:
        expected = test_case.find("expected")
        if expected is None:
            return {}
        return {child.tag: (child.text or "") for child in expected}

    # ── Login ───────────────────────────────────────────────────────────────

    def load_login_test_data(self) -> List[Dict[str, Any]]:
        root = self._parse_file("login_test_data.xml")
        results = []
        for tc in root.findall(".//TestCase"):
            results.append({
                "id":          tc.get("id"),
                "type":        tc.get("type"),
                "description": self._text(tc, "description"),
                "email":       self._text(tc, "email"),
                "password":    self._text(tc, "password"),
                "expected":    self._build_expected(tc),
            })
        return results

    def load_login_test_data_by_type(self, test_type: str) -> List[Dict[str, Any]]:
        return [t for t in self.load_login_test_data() if t.get("type") == test_type]

    # ── Registration ────────────────────────────────────────────────────────

    def load_registration_test_data(self) -> List[Dict[str, Any]]:
        root = self._parse_file("registration_test_data.xml")
        results = []
        for tc in root.findall(".//TestCase"):
            results.append({
                "id":          tc.get("id"),
                "type":        tc.get("type"),
                "description": self._text(tc, "description"),
                "role":        self._text(tc, "role"),
                "name":        self._text(tc, "name"),
                "email":       self._text(tc, "email"),
                "password":    self._text(tc, "password"),
                "expected":    self._build_expected(tc),
            })
        return results

    def load_registration_test_data_by_type(self, test_type: str) -> List[Dict[str, Any]]:
        return [t for t in self.load_registration_test_data() if t.get("type") == test_type]

    # ── Donation ────────────────────────────────────────────────────────────

    def load_donation_test_data(self) -> List[Dict[str, Any]]:
        root = self._parse_file("donation_test_data.xml")
        results = []
        for tc in root.findall(".//TestCase"):
            results.append({
                "id":          tc.get("id"),
                "type":        tc.get("type"),
                "description": self._text(tc, "description"),
                "title":       self._text(tc, "title"),
                "description_field": self._text(tc, "description"),
                "category":    self._text(tc, "category"),
                "quantity":    self._text(tc, "quantity") or "1",
                "pickupStart": self._text(tc, "pickupStart"),
                "pickupEnd":   self._text(tc, "pickupEnd"),
                "expected":    self._build_expected(tc),
            })
        return results

    def load_donation_test_data_by_type(self, test_type: str) -> List[Dict[str, Any]]:
        return [t for t in self.load_donation_test_data() if t.get("type") == test_type]


# Singleton instance used by all test modules
xml_parser = XMLTestDataParser()
