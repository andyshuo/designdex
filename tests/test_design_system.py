"""Tests for the design system generator and its two renderers."""

from designdex.design_system import (
    DesignSystemGenerator,
    format_ascii_box,
    format_markdown,
    generate_design_system,
    persist_design_system,
)


def test_generate_returns_every_documented_section():
    system = DesignSystemGenerator().generate("fintech dashboard", "Ledger")

    assert system["project_name"] == "Ledger"
    assert system["category"]
    for section in ("pattern", "style", "colors", "typography"):
        assert isinstance(system[section], dict)
    assert system["colors"]["primary"].startswith("#")


def test_generate_without_a_project_name_falls_back_to_the_query():
    system = DesignSystemGenerator().generate("fintech dashboard")

    assert system["project_name"] == "FINTECH DASHBOARD"


def test_a_known_product_category_pulls_in_its_reasoning_rule():
    """The product table decides the category, which decides the rule."""
    system = DesignSystemGenerator().generate("ecommerce checkout")

    assert system["category"] != "General"
    assert system["pattern"]["name"]


def test_persist_writes_master_and_page_files(tmp_path):
    system = DesignSystemGenerator().generate("fintech dashboard", "Ledger")

    info = persist_design_system(
        system,
        page="Settings",
        output_dir=str(tmp_path),
        page_query="settings page",
    )

    master = tmp_path / "design-system" / "ledger" / "MASTER.md"
    page = tmp_path / "design-system" / "ledger" / "pages" / "settings.md"

    assert info["status"] == "success"
    assert master.is_file()
    assert page.is_file()
    assert info["created_files"] == [str(master), str(page)]


def test_persist_without_a_page_writes_only_master(tmp_path):
    system = DesignSystemGenerator().generate("fintech dashboard", "Ledger")

    info = persist_design_system(system, output_dir=str(tmp_path))

    assert len(info["created_files"]) == 1


def test_persist_is_idempotent(tmp_path):
    """Running twice must overwrite, not append."""
    system = DesignSystemGenerator().generate("fintech dashboard", "Ledger")

    persist_design_system(system, output_dir=str(tmp_path))
    master = tmp_path / "design-system" / "ledger" / "MASTER.md"
    first = master.read_text(encoding="utf-8")

    persist_design_system(system, output_dir=str(tmp_path))

    assert master.read_text(encoding="utf-8") == first


def test_the_two_renderers_produce_different_output():
    system = DesignSystemGenerator().generate("fintech dashboard", "Ledger")

    assert format_ascii_box(system) != format_markdown(system)


def test_markdown_rendering_is_markdown():
    system = DesignSystemGenerator().generate("fintech dashboard", "Ledger")

    assert format_markdown(system).lstrip().startswith("#")


def test_generate_design_system_returns_the_requested_format():
    markdown = generate_design_system("fintech dashboard", "Ledger", "markdown")

    assert markdown.lstrip().startswith("#")


def test_generate_design_system_can_persist(tmp_path):
    generate_design_system(
        "fintech dashboard", "Ledger", persist=True, output_dir=str(tmp_path)
    )

    assert (tmp_path / "design-system" / "ledger" / "MASTER.md").is_file()
