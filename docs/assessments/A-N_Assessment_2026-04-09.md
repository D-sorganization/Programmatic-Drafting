# Comprehensive A-N Codebase Assessment

**Date**: 2026-04-09
**Scope**: Complete adversarial and detailed review targeting extreme quality levels.
**Reviewer**: Automated scheduled comprehensive review

## 1. Executive Summary

**Overall Grade: C**

Programmatic-Drafting has 28 source files, 9 tests (0.32 ratio — **low**), and 2 monolith files. The preview rendering scene is 739 LOC; the drafter window is 557 LOC.

| Metric | Value |
|---|---|
| Source files | 28 |
| Test files | 9 |
| Source LOC | 4,818 |
| Test/Src ratio | 0.32 |
| Monolith files (>500 LOC) | 2 |

## 2. Key Factor Findings

### DRY — Grade B-
- `vessel_drafter_scene.py` and `vessel_drafter_window.py` likely share geometry/coordinate transforms that could be extracted.

### DbC — Grade C-
- Drafting operations lack dimensional/unit invariants.

### TDD — Grade D+
- Ratio 0.32 is poor for CAD-style code where regression visual-diffs are hard to catch.

### Orthogonality — Grade C
- Preview scene mixes 3D rendering with data model (likely).

### Reusability — Grade C+
- Single-project code; reuse goals are limited.

### Changeability — Grade C
- Low test ratio makes refactoring risky.

### LOD — Grade B
- Unknown; not spot-checked.

### Function Size / Monoliths
- `src/programmatic_drafting/preview/vessel_drafter_scene.py` — **739 LOC**
- `src/programmatic_drafting/gui/vessel_drafter_window.py` — 557 LOC
- `src/programmatic_drafting/models/vessel_drafter.py` — 440 LOC (watch)

## 3. Recommended Remediation Plan

1. **P0**: Decompose `vessel_drafter_scene.py` (739 LOC) into `scene.py`, `camera.py`, `geometry.py`, `materials.py`.
2. **P0**: Raise test-to-source ratio to ≥0.60 — add unit tests for vessel_drafter model.
3. **P1**: Refactor `vessel_drafter_window.py` (557 LOC) to extract command handling from view.
4. **P1**: Add DbC contracts for vessel dimensions (positive, unit-consistent).
5. **P2**: Add golden/snapshot tests for preview rendering.
