"""Tests for picking the right table from a free-text query."""

import pytest

from uiux_pro_max.core import detect_domain


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("minimalism glassmorphism dark mode", "style"),
        ("wcag keyboard navigation touch target", "ux"),
        ("serif heading font pairing", "typography"),
        ("lucide heroicons picture", "icons"),
        ("bar chart trend heatmap", "chart"),
        ("hero testimonial pricing section", "landing"),
        ("saas fintech crypto dashboard", "product"),
        ("useeffect memo dynamic import", "react"),
        ("aria focus outline semantic", "web"),
        ("hex palette rgb", "color"),
    ],
)
def test_detects_the_intended_domain(query, expected):
    assert detect_domain(query) == expected


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("a guide to icon libraries", "icons"),
        ("sidebar navigation", "ux"),
        ("building a pricing table", "landing"),
    ],
)
def test_keywords_only_match_at_a_word_start(query, expected):
    """Substring matching sent whole queries to the wrong table.

    "guide" contains "ui" and "sidebar" contains "bar", so a plain ``in`` test
    answered ``style`` and ``chart`` for queries that were plainly about icons
    and about navigation.
    """
    assert detect_domain(query) == expected


def test_a_plural_still_finds_its_singular_keyword():
    """Requiring a word start must not cost us the trailing "s"."""
    assert detect_domain("charts") == "chart"


def test_material_with_no_keywords_falls_back_to_style():
    assert detect_domain("qwertyuiop") == "style"


def test_detection_is_case_insensitive():
    assert detect_domain("DARK MODE") == detect_domain("dark mode")
