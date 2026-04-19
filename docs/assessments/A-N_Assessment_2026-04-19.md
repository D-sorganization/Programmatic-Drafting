# A-N Assessment - Programmatic-Drafting - 2026-04-19

Run time: 2026-04-19T08:02:24.4668879Z UTC
Sync status: synced
Sync notes: Already up to date.
From https://github.com/D-sorganization/Programmatic-Drafting
 * branch            fix/issue-32-vessel-drafter-model-split -> FETCH_HEAD

Overall grade: C (76/100)

## Coverage Notes
- Reviewed tracked first-party files from git ls-files, excluding cache, build, vendor, virtualenv, temp, and generated output directories.
- Reviewed 87 tracked files, including 67 code files, 24 test files, 6 CI files, 1 config/build files, and 10 docs/onboarding files.
- This is a read-only static assessment of committed files. TDD history and confirmed Law of Demeter semantics require commit-history review and deeper call-graph analysis; this report distinguishes those limits from confirmed file evidence.

## Category Grades
### A. Architecture and Boundaries: B (82/100)
Assesses source organization and boundary clarity from tracked first-party layout.
- Evidence: `87 tracked first-party files`
- Evidence: `43 files under source-like directories`

### B. Build and Dependency Management: C (72/100)
Assesses committed build, dependency, and tool configuration.
- Evidence: `pyproject.toml`

### C. Configuration and Environment Hygiene: C (78/100)
Checks whether runtime and developer configuration is explicit.
- Evidence: `pyproject.toml`

### D. Contracts, Types, and Domain Modeling: B (82/100)
Design by Contract evidence includes validation, assertions, typed models, explicit raised errors, and invariants.
- Evidence: `src/programmatic_drafting/analysis/vessel_drafter_metrics.py`
- Evidence: `src/programmatic_drafting/contracts.py`
- Evidence: `src/programmatic_drafting/gui/vessel_drafter_port_panel.py`
- Evidence: `src/programmatic_drafting/gui/vessel_drafter_window.py`
- Evidence: `src/programmatic_drafting/models/cylindrical_bath.py`
- Evidence: `src/programmatic_drafting/models/electrode_advisor.py`
- Evidence: `src/programmatic_drafting/models/ports.py`
- Evidence: `src/programmatic_drafting/models/vessel_drafter.py`
- Evidence: `src/programmatic_drafting/models/vessel_drafter_types.py`
- Evidence: `src/programmatic_drafting/models/vessel_materials.py`

### E. Reliability and Error Handling: C (76/100)
Reliability is graded from test presence plus explicit validation/error-handling signals.
- Evidence: `tests/test_cli.py`
- Evidence: `tests/test_constants.py`
- Evidence: `tests/test_cylindrical_bath_layout.py`
- Evidence: `tests/test_cylindrical_bath_manifest.py`
- Evidence: `tests/test_electrode_advisor_defaults.py`
- Evidence: `src/programmatic_drafting/analysis/vessel_drafter_metrics.py`
- Evidence: `src/programmatic_drafting/contracts.py`
- Evidence: `src/programmatic_drafting/gui/vessel_drafter_port_panel.py`
- Evidence: `src/programmatic_drafting/gui/vessel_drafter_window.py`
- Evidence: `src/programmatic_drafting/models/cylindrical_bath.py`

### F. Function, Module Size, and SRP: C (70/100)
Evaluates function size, script/module size, and single responsibility using static size signals.
- Evidence: `tests/test_vessel_drafter_scene_meshes.py (513 lines)`
- Evidence: `src/programmatic_drafting/models/vessel_materials.py (coarse avg 104 lines/definition)`

### G. Testing and TDD Posture: B (82/100)
TDD history cannot be confirmed statically; grade reflects committed automated test posture.
- Evidence: `tests/test_cli.py`
- Evidence: `tests/test_constants.py`
- Evidence: `tests/test_cylindrical_bath_layout.py`
- Evidence: `tests/test_cylindrical_bath_manifest.py`
- Evidence: `tests/test_electrode_advisor_defaults.py`
- Evidence: `tests/test_electrode_advisor_manifest.py`
- Evidence: `tests/test_step_export.py`
- Evidence: `tests/test_vessel_drafter_defaults.py`
- Evidence: `tests/test_vessel_drafter_export.py`
- Evidence: `tests/test_vessel_drafter_geometry.py`
- Evidence: `tests/test_vessel_drafter_gui.py`
- Evidence: `tests/test_vessel_drafter_manifest.py`

### H. CI/CD and Automation: C (78/100)
Checks for tracked CI/CD workflow files.
- Evidence: `.github/workflows/ci-failure-digest.yml`
- Evidence: `.github/workflows/ci-standard.yml`
- Evidence: `.github/workflows/pr-auto-labeler.yml`
- Evidence: `.github/workflows/pr-size-check.yml`
- Evidence: `.github/workflows/stale-cleanup.yml`
- Evidence: `.github/workflows/weekly-cad-sweep.yml`

### I. Security and Secret Hygiene: B (82/100)
Secret scan is regex-based; findings require manual confirmation.
- Evidence: No direct tracked-file evidence found for this category.

### J. Documentation and Onboarding: B (82/100)
Checks docs, README, onboarding, and release documents.
- Evidence: `README.md`
- Evidence: `docs/assessments/A-N_Assessment_2026-04-02.md`
- Evidence: `docs/assessments/A-N_Assessment_2026-04-04.md`
- Evidence: `docs/assessments/A-N_Assessment_2026-04-09.md`
- Evidence: `docs/assessments/A-N_Assessment_2026-04-10.md`
- Evidence: `docs/assessments/A-N_Assessment_2026-04-11.md`
- Evidence: `docs/projects/cylindrical_bath_layout.md`
- Evidence: `docs/projects/electrode_advisor_default_layout.md`
- Evidence: `docs/projects/vessel_drafter_default.md`
- Evidence: `docs/repo-outline.md`

### K. Maintainability, DRY, and Duplication: B (80/100)
DRY is assessed through duplicate filename clusters and TODO/FIXME density as static heuristics.
- Evidence: No direct tracked-file evidence found for this category.

### L. API Surface and Law of Demeter: D (68/100)
Law of Demeter is approximated with deep member-chain hints; confirmed violations require semantic review.
- Evidence: `src/programmatic_drafting/gui/vessel_drafter_preview_panel.py`
- Evidence: `src/programmatic_drafting/gui/vessel_drafter_window.py`
- Evidence: `src/programmatic_drafting/gui/vessel_drafter_window_controls.py`

### M. Observability and Operability: C (74/100)
Checks for logging, metrics, monitoring, and operational artifacts.
- Evidence: `src/programmatic_drafting/analysis/vessel_drafter_metrics.py`
- Evidence: `tests/test_vessel_drafter_metrics.py`

### N. Governance, Licensing, and Release Hygiene: F (52/100)
Checks ownership, release, contribution, security, and license metadata.
- Evidence: No direct tracked-file evidence found for this category.

## Explicit Engineering Practice Review
- TDD: Automated tests are present, but red-green-refactor history is not confirmable from static files.
- DRY: No repeated filename clusters met the static threshold.
- Design by Contract: Validation/contract signals were found in tracked code.
- Law of Demeter: Deep member-chain hints were found and should be semantically reviewed.
- Function size and SRP: Large modules or coarse long-definition signals were found.

## Key Risks
- Large modules/scripts reduce maintainability and SRP clarity.

## Prioritized Remediation Recommendations
1. Split the largest modules by responsibility and add characterization tests before refactoring.

## Actionable Issue Candidates
### Split oversized modules by responsibility
- Severity: medium
- Problem: Oversized files found: tests/test_vessel_drafter_scene_meshes.py (513 lines)
- Evidence: Category F lists files over 500 lines or coarse long-definition signals.
- Impact: Large modules obscure ownership, complicate review, and weaken SRP.
- Proposed fix: Add characterization tests, then split cohesive responsibilities into smaller modules.
- Acceptance criteria: Largest files are reduced or justified; extracted modules have focused tests.
- Expectations: SRP, function size, module size, maintainability

