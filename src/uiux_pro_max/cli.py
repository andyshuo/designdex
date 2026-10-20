"""Command line interface for the design knowledge base."""

from __future__ import annotations

import argparse
import io
import json
import sys

from .core import AVAILABLE_STACKS, CSV_CONFIG, MAX_RESULTS, search, search_stack
from .design_system import (
    DesignSystemGenerator,
    format_ascii_box,
    format_markdown,
    persist_design_system,
)

#: Field values longer than this are truncated in the human-readable output.
#: The rows carry a lot of prose, and most of it is not needed to pick a style.
MAX_FIELD_CHARS = 300


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser.

    Split out from :func:`main` so the flags can be inspected in tests without
    running anything.
    """
    parser = argparse.ArgumentParser(
        prog="uiux-pro-max",
        description="Search a curated UI/UX design knowledge base.",
    )
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "--domain",
        "-d",
        choices=list(CSV_CONFIG.keys()),
        help="Restrict the search to one domain",
    )
    parser.add_argument(
        "--stack",
        "-s",
        choices=AVAILABLE_STACKS,
        help="Search stack-specific guidelines instead of a domain",
    )
    parser.add_argument(
        "--max-results",
        "-n",
        type=int,
        default=MAX_RESULTS,
        help=f"Max results (default: {MAX_RESULTS})",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--design-system",
        "-ds",
        action="store_true",
        help="Generate a complete design system recommendation",
    )
    parser.add_argument(
        "--project-name",
        "-p",
        default=None,
        help="Project name used in design system output",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["ascii", "markdown"],
        default="ascii",
        help="Output format for the design system",
    )
    parser.add_argument(
        "--persist",
        action="store_true",
        help="Write the design system to design-system/<project>/MASTER.md",
    )
    parser.add_argument(
        "--page",
        default=None,
        help="Also write a page-specific override file",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default=None,
        help="Output directory for persisted files (default: current directory)",
    )
    return parser


def format_output(result: dict) -> str:
    """Render a search result as Markdown."""
    if "error" in result:
        return f"Error: {result['error']}"

    output = []
    if result.get("stack"):
        output.append("## UI Pro Max Stack Guidelines")
        output.append(f"**Stack:** {result['stack']} | **Query:** {result['query']}")
    else:
        output.append("## UI Pro Max Search Results")
        output.append(f"**Domain:** {result['domain']} | **Query:** {result['query']}")
    output.append(
        f"**Source:** {result['file']} | **Found:** {result['count']} results\n"
    )

    for i, row in enumerate(result["results"], 1):
        output.append(f"### Result {i}")
        for key, value in row.items():
            value_str = str(value)
            if len(value_str) > MAX_FIELD_CHARS:
                value_str = value_str[:MAX_FIELD_CHARS] + "..."
            output.append(f"- **{key}:** {value_str}")
        output.append("")

    return "\n".join(output)


def force_utf8_stdio() -> None:
    """Re-wrap stdout and stderr as UTF-8.

    The corpus contains emoji and the Windows console defaults to cp1252, which
    raises ``UnicodeEncodeError`` on the first arrow. Called from :func:`main`
    rather than at import time so importing this module stays side-effect free.
    """
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def _report_persisted(info: dict, page: str | None) -> None:
    """Print where the design system landed."""
    if info.get("status") != "success":
        return
    print()
    print("=" * 60)
    print(f"Design system persisted to {info['design_system_dir']}/")
    for path in info["created_files"]:
        print(f"  {path}")
    print()
    print("When building a page, check its override file first.")
    print("If it exists, its rules override MASTER.md. Otherwise use MASTER.md.")
    print("=" * 60)


def main(argv: list[str] | None = None) -> int:
    """Run the CLI. Returns the process exit code."""
    force_utf8_stdio()
    args = build_parser().parse_args(argv)

    if args.design_system:
        system = DesignSystemGenerator().generate(args.query, args.project_name)
        info = None
        if args.persist:
            info = persist_design_system(system, args.page, args.output_dir, args.query)
        if args.format == "markdown":
            print(format_markdown(system))
        else:
            print(format_ascii_box(system))
        if info:
            _report_persisted(info, args.page)
        return 0

    if args.stack:
        result = search_stack(args.query, args.stack, args.max_results)
    else:
        result = search(args.query, args.domain, args.max_results)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_output(result))

    return 1 if "error" in result else 0
