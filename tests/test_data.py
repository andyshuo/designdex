"""Tests that the shipped corpus matches the configuration that describes it.

Every column named in ``CSV_CONFIG`` or ``STACK_CONFIG`` has to exist in the
corresponding CSV, otherwise a search silently returns rows full of empty
strings long after the data was edited.
"""

import csv

import pytest

from uiux_pro_max.core import _STACK_COLS, CSV_CONFIG, DATA_DIR, STACK_CONFIG


def _header(path):
    with open(path, encoding="utf-8") as handle:
        return next(csv.reader(handle))


def test_every_domain_file_exists():
    missing = [
        config["file"]
        for config in CSV_CONFIG.values()
        if not (DATA_DIR / config["file"]).is_file()
    ]

    assert missing == []


def test_every_stack_file_exists():
    missing = [
        config["file"]
        for config in STACK_CONFIG.values()
        if not (DATA_DIR / config["file"]).is_file()
    ]

    assert missing == []


@pytest.mark.parametrize("domain", sorted(CSV_CONFIG))
def test_domain_file_has_every_configured_column(domain):
    config = CSV_CONFIG[domain]
    header = _header(DATA_DIR / config["file"])
    wanted = config["search_cols"] + config["output_cols"]

    assert [column for column in wanted if column not in header] == []


@pytest.mark.parametrize("stack", sorted(STACK_CONFIG))
def test_stack_file_has_every_configured_column(stack):
    header = _header(DATA_DIR / STACK_CONFIG[stack]["file"])
    wanted = _STACK_COLS["search_cols"] + _STACK_COLS["output_cols"]

    assert [column for column in wanted if column not in header] == []


@pytest.mark.parametrize("domain", sorted(CSV_CONFIG))
def test_domain_file_is_not_empty(domain):
    with open(DATA_DIR / CSV_CONFIG[domain]["file"], encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert rows


@pytest.mark.parametrize("domain", sorted(CSV_CONFIG))
def test_the_first_column_has_no_byte_order_mark(domain):
    """A BOM would silently rename the first column for every reader."""
    header = _header(DATA_DIR / CSV_CONFIG[domain]["file"])

    assert not header[0].startswith("\ufeff")
