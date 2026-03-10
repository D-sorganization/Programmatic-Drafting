"""CLI for generating drafting artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

from programmatic_drafting.exporters.step_export import export_default_layout_step


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Programmatic drafting CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser(
        "export-electrode-advisor-default",
        help="Export the default electrode advisor STEP artifact.",
    )
    export_parser.add_argument(
        "--output",
        default="generated/electrode_advisor_default/electrode_advisor_default_layout.step",
        help="STEP output path.",
    )
    export_parser.add_argument(
        "--manifest",
        default="generated/electrode_advisor_default/electrode_advisor_default_layout.json",
        help="JSON manifest output path.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "export-electrode-advisor-default":
        step_path = export_default_layout_step(
            output_path=Path(args.output),
            manifest_path=Path(args.manifest),
        )
        print(step_path)
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
