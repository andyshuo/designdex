"""Tests for the command line interface."""

import json

import pytest

from uiux_pro_max.cli import build_parser, format_output, main
from uiux_pro_max.core import search


def test_format_output_lists_each_result():
    text = format_output(search("dashboard", "product", 1))

    assert "## UI Pro Max Search Results" in text
    assert "### Result 1" in text


def test_format_output_labels_a_stack_search():
    text = format_output(search("useState", max_results=1) | {"stack": "react"})

    assert "## UI Pro Max Stack Guidelines" in text
    assert "**Stack:** react" in text


def test_format_output_renders_an_error():
    assert format_output({"error": "boom"}) == "Error: boom"


def test_the_parser_rejects_an_unknown_domain():
    with pytest.raises(SystemExit):
        build_parser().parse_args(["query", "--domain", "nonsense"])


def test_main_returns_zero_for_a_good_query(capsys):
    assert main(["dashboard"]) == 0

    assert capsys.readouterr().out.strip()


def test_main_prints_json_when_asked(capsys):
    assert main(["dashboard", "-n", "1", "--json"]) == 0

    data = json.loads(capsys.readouterr().out)

    assert data["count"] == 1


def test_main_searches_a_stack(capsys):
    assert main(["useState", "-s", "react"]) == 0

    assert "stacks/react.csv" in capsys.readouterr().out


def test_main_generates_a_design_system(capsys):
    assert main(["fintech", "-ds"]) == 0

    assert capsys.readouterr().out.strip()


def test_main_renders_the_design_system_as_markdown(capsys):
    assert main(["fintech", "-ds", "-f", "markdown"]) == 0

    assert capsys.readouterr().out.lstrip().startswith("#")


def test_main_persists_into_the_output_dir(tmp_path, capsys):
    assert main(["fintech", "-ds", "--persist", "-o", str(tmp_path)]) == 0

    assert (tmp_path / "design-system" / "fintech" / "MASTER.md").is_file()


def test_persist_confirmation_names_the_directory_it_actually_wrote(tmp_path, capsys):
    """The confirmation used to print ``design-system/default/`` while the files
    went somewhere else entirely, because the folder name comes from the
    generated project name, not from the (optional) ``--project-name`` flag.
    """
    main(["fintech", "-ds", "--persist", "-o", str(tmp_path)])
    out = capsys.readouterr().out

    real = tmp_path / "design-system" / "fintech"
    assert real.is_dir()
    assert str(real) in out


def test_main_writes_a_page_override(tmp_path, capsys):
    assert (
        main(
            [
                "fintech",
                "-ds",
                "--persist",
                "-p",
                "Ledger",
                "--page",
                "Settings",
                "-o",
                str(tmp_path),
            ]
        )
        == 0
    )

    assert (tmp_path / "design-system" / "ledger" / "pages" / "settings.md").is_file()
