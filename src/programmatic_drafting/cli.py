"""CLI for generating drafting artifacts."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from programmatic_drafting.exporters.step_export import (
    export_cylindrical_bath_layout_step,
    export_default_layout_step,
    export_vessel_drafter_default_step,
)

logger = logging.getLogger(__name__)


def _add_export_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    name: str,
    help_text: str,
    default_output: str,
    default_manifest: str,
) -> None:
    """Register a STEP export command with shared output/manifest flags."""
    command_parser = subparsers.add_parser(name, help=help_text)
    command_parser.add_argument(
        "--output",
        default=default_output,
        help="STEP output path.",
    )
    command_parser.add_argument(
        "--manifest",
        default=default_manifest,
        help="JSON manifest output path.",
    )


def _add_export_commands(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Register all STEP export subcommands."""
    _add_export_command(
        subparsers,
        "export-electrode-advisor-default",
        "Export the default electrode advisor STEP artifact.",
        "generated/electrode_advisor_default/electrode_advisor_default_layout.step",
        "generated/electrode_advisor_default/electrode_advisor_default_layout.json",
    )
    _add_export_command(
        subparsers,
        "export-cylindrical-bath-layout",
        "Export the cylindrical bath radial-electrode STEP artifact.",
        "generated/cylindrical_bath_layout/cylindrical_bath_layout.step",
        "generated/cylindrical_bath_layout/cylindrical_bath_layout.json",
    )
    _add_export_command(
        subparsers,
        "export-vessel-drafter-default",
        "Export the default vessel drafter STEP artifact.",
        "generated/vessel_drafter_default/vessel_drafter_default.step",
        "generated/vessel_drafter_default/vessel_drafter_default.json",
    )


def _add_gui_commands(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Register GUI launcher subcommands."""
    subparsers.add_parser(
        "launch-vessel-drafter-gui",
        help="Launch the PyQt6 vessel drafter GUI.",
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser from focused command-registration helpers."""
    parser = argparse.ArgumentParser(description="Programmatic drafting CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    _add_export_commands(subparsers)
    _add_gui_commands(subparsers)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "export-electrode-advisor-default":
        step_path = export_default_layout_step(
            output_path=Path(args.output),
            manifest_path=Path(args.manifest),
        )
        logger.info("Exported electrode advisor STEP artifact to %s", step_path)
        return 0

    if args.command == "export-cylindrical-bath-layout":
        step_path = export_cylindrical_bath_layout_step(
            output_path=Path(args.output),
            manifest_path=Path(args.manifest),
        )
        logger.info("Exported cylindrical bath STEP artifact to %s", step_path)
        return 0

    if args.command == "export-vessel-drafter-default":
        step_path = export_vessel_drafter_default_step(
            output_path=Path(args.output),
            manifest_path=Path(args.manifest),
        )
        logger.info("Exported vessel drafter STEP artifact to %s", step_path)
        return 0

    if args.command == "launch-vessel-drafter-gui":
        from programmatic_drafting.gui.vessel_drafter_window import (
            launch as launch_vessel_drafter,
        )

        return launch_vessel_drafter()

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
