"""Tests for the domain and stack search entry points."""

from designdex.core import CSV_CONFIG, MAX_RESULTS, search, search_stack


def test_search_returns_rows_with_the_configured_columns():
    result = search("bar chart", "chart", 2)

    assert result["domain"] == "chart"
    assert result["file"] == "charts.csv"
    assert 0 < result["count"] <= 2
    assert set(result["results"][0]) <= set(CSV_CONFIG["chart"]["output_cols"])


def test_search_defaults_to_three_results():
    result = search("dashboard", "product")

    assert result["count"] <= MAX_RESULTS


def test_search_honours_max_results():
    assert search("dashboard", "product", 1)["count"] == 1


def test_search_with_zero_max_results_returns_nothing():
    assert search("dashboard", "product", 0)["count"] == 0


def test_search_with_negative_max_results_returns_nothing():
    """A negative count used to slice from the end of the ranking.

    ``ranked[:-1]`` silently returned every row but the last, so ``-n -1`` was
    the opposite of what anyone would expect.
    """
    assert search("dashboard", "product", -1)["count"] == 0


def test_unknown_domain_is_an_error_rather_than_a_silent_fallback():
    """A typo used to fall through to the style table without saying so."""
    result = search("anything", "nonsense")

    assert "error" in result
    assert "nonsense" in result["error"]


def test_search_without_a_domain_detects_one():
    assert search("lucide icon set")["domain"] == "icons"


def test_stack_search_returns_guidelines_for_that_stack():
    result = search_stack("useState", "react", 2)

    assert result["stack"] == "react"
    assert result["file"] == "stacks/react.csv"
    assert 0 < result["count"] <= 2


def test_unknown_stack_is_an_error():
    result = search_stack("useState", "cobol")

    assert "error" in result
    assert "cobol" in result["error"]
