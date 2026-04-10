# Comprehensive A-N Codebase Assessment

**Date**: 2026-04-09
**Scope**: Complete adversarial and detailed review targeting extreme quality levels.
**Reviewer**: Automated scheduled comprehensive review (parallel deep-dive)

## 1. Executive Summary

**Overall Grade: B+**

Programmatic-Drafting excels at architecture, validation, and separation of concerns. Primary weakness: **test coverage is only 0.16** (test LOC / source LOC), with large modules (`vessel_drafter_profiles.py` 184 LOC, `vessel_drafter_rendering.py` 239 LOC, `vessel_drafter_scene.py` 740 LOC) lacking dedicated unit tests. DbC infrastructure is strong.

| Metric | Value |
|---|---|
| Python source files | 28 |
| Test files | 9 |
| Source LOC | 4,146 |
| Test LOC | 672 |
| Total LOC | 4,818 |
| Test/Src ratio | **0.16** |

## 2. Key Factor Findings

### DRY — Grade B

**Strengths**
- `contracts.py` fully reusable across modules.
- Clean model/view separation.

**Issues**
1. `models/cylindrical_bath.py:9` — `MM_PER_INCH = 25.4` re-declared locally; `vessel_drafter.py:21` has the same constant. Fix: move to shared `constants.py`.
2. `models/vessel_drafter.py:102-140` — `VesselSidePort` and `VesselLidPort` both define duplicated `normalized_clock_angle_degrees`, `normalized_clock_angle_radians`, `radius_in` properties. Fix: extract a `PortMixin` or base dataclass.
3. `exporters/step_export.py:36-127` — three `export_*_step` functions share an identical pattern (mkdir → build shape → export_step → write manifest). Fix: extract generic `_export_layout_step` helper.
4. `models/vessel_drafter.py:25-59` — `MaterialLayer` delegates 8 properties to `MaterialProperties` one-by-one. Fix: use `__getattr__` delegation or composition.

### DbC — Grade A

**Strengths**
- Dedicated `contracts.py` with 6 reusable precondition helpers.
- `VesselDrafterLayout.__post_init__` has **18 validation calls** (lines 161-188).
- `VesselSidePort.__post_init__`, `VesselLidPort.__post_init__`, `MaterialProperties.__post_init__` all validate.
- Port constraint validation (`_validate_side_ports`, `_validate_lid_ports`) provides cross-field invariant checking.

**Issues**
- None significant. Excellent DbC implementation.

### TDD — Grade C

**Strengths**
- Tests cover defaults, geometry envelopes, round-trips, validation errors, GUI behavior (5 tests), preview data, metrics, STEP export.

**Issues**
1. **Test ratio 0.16 is far below target.**
2. `projects/vessel_drafter_profiles.py` (184 LOC of elliptical head math) — **untested independently.**
3. `gui/vessel_drafter_rendering.py` (239 LOC) — untested.
4. `preview/vessel_drafter_scene.py` (740 LOC) — only a few scene-level checks in `test_vessel_drafter_metrics.py`.
5. `preview/vessel_drafter_scene.py:549-577` — ear-clipping triangulation (`_triangulate_profile_loop`) untested.

**Fix**: Add dedicated unit tests for profile point generation, boundary loops, triangulation, rendering.

### Orthogonality — Grade A

**Strengths**
- Clean separation: `models/` (data + validation), `projects/` (geometry), `preview/` (view data), `gui/` (UI), `exporters/` (serialization), `analysis/` (metrics).
- Each module single-purpose. Models don't know about rendering; preview doesn't know about STEP.

**Issues**
- None significant.

### Reusability — Grade B

**Strengths**
- `contracts.py` fully generic.
- `ZoomableGraphicsView`, `PortTableSection`, `PortValueDialog` reusable widgets.
- `build_vessel_3d_scene` parameterized with layout + view options.

**Issues**
1. `build_default_layout_shape` and `build_cylindrical_bath_layout_shape` are hardcoded to specific geometry types — no shared shape-building protocol.

### Changeability — Grade A

**Strengths**
- All geometry driven by `VesselDrafterLayout` / `CylindricalBathLayout` dataclasses.
- Adding materials: extend `DEFAULT_VESSEL_MATERIALS` + `layers` property.
- GUI reads/writes layout objects cleanly.

**Issues**
- None significant.

### LOD — Grade A

- No deep chain calls into foreign objects.
- `VesselComponent` flattens properties at construction time (not delegated at render time).
- Port objects call `centerline_height_in(layout)` rather than reaching through layers.

### Function Size — Grade B

**Issues**
1. `preview/vessel_drafter_scene.py:129-163` — `_build_shell_meshes` 34 LOC (borderline).
2. `preview/vessel_drafter_scene.py:299-354` — `_revolved_profile_mesh` 55 LOC. Fix: split vertex/face generation.
3. `preview/vessel_drafter_scene.py:414-480` — `_cylinder_mesh` 66 LOC. Fix: extract cap generation.
4. `gui/vessel_drafter_window.py:62-112` — `VesselDrafterWindow.__init__` 50 LOC (GUI constructor, expected).
5. `gui/vessel_drafter_rendering.py:24-97` — `render_cross_section` 73 LOC. Fix: split into band/electrode/port rendering helpers.

### Script Monoliths — Grade A

- Largest file: `vessel_drafter_scene.py` (740 LOC) — justified by mesh math but could split triangulation.
- No other monoliths.

## 3. Specific Issues Summary

| File | Lines | Issue | Principle |
|---|---|---|---|
| `models/cylindrical_bath.py` | 9 | `MM_PER_INCH` duplicated | DRY |
| `models/vessel_drafter.py` | 25-59 | `MaterialLayer` verbose delegation | DRY |
| `models/vessel_drafter.py` | 102-140 | Port classes duplicate angle/radius properties | DRY |
| `exporters/step_export.py` | 36-127 | 3 export functions share identical pattern | DRY |
| `preview/vessel_drafter_scene.py` | 299-354 | `_revolved_profile_mesh` 55 LOC | Function Size |
| `preview/vessel_drafter_scene.py` | 414-480 | `_cylinder_mesh` 66 LOC | Function Size |
| `gui/vessel_drafter_rendering.py` | 24-97 | `render_cross_section` 73 LOC | Function Size |
| `projects/vessel_drafter_profiles.py` | 1-184 | No dedicated unit tests | TDD |
| `preview/vessel_drafter_scene.py` | 549-577 | Ear-clipping triangulation untested | TDD |

## 4. Recommended Remediation Plan

1. **P0 (TDD)**: Add unit tests for `vessel_drafter_profiles.py`, triangulation, rendering. Raise test ratio to ≥0.50.
2. **P1 (DRY)**: Extract `PortMixin` base; unify `MM_PER_INCH` constant; extract STEP export helper.
3. **P1 (Function Size)**: Split `_cylinder_mesh`, `_revolved_profile_mesh`, `render_cross_section`.
4. **P2 (Reusability)**: Define a shape-building protocol for layout → shape conversion.
