# Programmatic Drafting

Programmatic STEP drafting for D-sorganization projects.

This repo is the CAD automation home for inspectable geometry exports that can be
generated in CI and opened in FreeCAD locally. The first tracked project is the
default electrode advisor layout from the current web tool.

## Why this repo exists

- Keeps CAD automation separate from application repos.
- Uses code as the source of truth for geometry and exports reproducible STEP files.
- Makes STEP generation CI-friendly instead of depending on a desktop FreeCAD install.

## Current project

- `electrode_advisor_default_layout`
  - Source of truth: `Tools/src/electrode_advisor/web/src/components/GlassBath3DViewer.tsx`
  - Default bath: rectangular, `3.0 m x 2.0 m x 2.5 m`
  - Default glass level: `1.5 m`
  - Default electrodes: `3`
  - Default electrode length: `1500 mm`
  - Default worn length: `150 mm`
  - Default operating current: `2500 A`

Generated artifacts:

- `generated/electrode_advisor_default/electrode_advisor_default_layout.step`
- `generated/electrode_advisor_default/electrode_advisor_default_layout.json`

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python -m programmatic_drafting.cli export-electrode-advisor-default
```

Open the generated STEP file in FreeCAD for inspection.

## Repo Outline

- `src/programmatic_drafting/models/`
  - Geometry inputs and source-of-truth defaults copied from product code.
- `src/programmatic_drafting/projects/`
  - Concrete drafting projects and shape builders.
- `src/programmatic_drafting/exporters/`
  - STEP export utilities and manifest writers.
- `tests/`
  - Contract tests for default values, layout math, and STEP export.
- `docs/projects/`
  - Project-specific drafting notes and geometry assumptions.
- `.github/workflows/`
  - Fleet-style CI, PR hygiene, and weekly CAD validation.

## CAD Strategy

- Primary kernel: `build123d`
- Export format: STEP
- Inspection target: FreeCAD
- Coordinate convention in CAD: `Z` up
- Coordinate convention in the source viewer: `Y` up

The drafting code applies a documented axis transform so the model opens in a
natural CAD orientation while still matching the tool layout.
