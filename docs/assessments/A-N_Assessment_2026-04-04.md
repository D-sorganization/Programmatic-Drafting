# Comprehensive A-N Codebase Assessment

**Date**: 2026-04-04
**Repo**: Programmatic-Drafting
**Scope**: Complete A-N review evaluating TDD, DRY, DbC, LOD compliance.

## Metrics
- Total Python files: 28
- Test files: 9
- Max file LOC: 739 (preview/vessel_drafter_scene.py)
- Monolithic files (>500 LOC): 2 (vessel_drafter_scene.py at 739, vessel_drafter_window.py at 557)
- CI workflow files: 6
- Print statements in src: 3
- DbC patterns in src: 18

## Grades Summary

| Category | Grade | Notes |
|----------|-------|-------|
| A: Code Structure | 8/10 | Well-organized package: models/, gui/, preview/, projects/, exporters/, analysis/. Clear separation of domain models from GUI rendering. contracts.py centralizes validation. |
| B: Documentation | 7/10 | Module-level docstrings present. contracts.py has clear function documentation. vessel_drafter.py uses frozen dataclasses with descriptive field names. Missing CLAUDE.md. Some GUI modules lack docstrings. |
| C: Test Coverage | 6/10 | 9 test files for 28 src files (0.32 ratio). Tests cover geometry, defaults, export, GUI, metrics, and preview. Missing tests for cli.py, vessel_materials.py, and several GUI modules. |
| D: Error Handling | 7/10 | contracts.py provides 6 validation functions (require_positive, require_nonnegative, require_fraction, require_integer_at_least, require_less_or_equal, require_finite). All raise ValueError with descriptive messages. Some GUI modules lack input validation. |
| E: Performance | 7/10 | vessel_drafter_scene.py uses @lru_cache for mesh generation. numpy for mesh vertex computation. Angular segments configurable for LOD. Scene mesh generation could benefit from lazy evaluation. |
| F: Security | 6/10 | No bandit scan visible. 3 print statements. STEP export uses CadQuery which loads geometry safely. No user-input file path sanitization visible. |
| G: Dependencies | 7/10 | Core depends on numpy. GUI on PyQt6/PySide. Export on CadQuery/OCP. Analysis on standard math. Clean optional dependency boundaries. |
| H: CI/CD | 7/10 | 6 workflows: ci-standard, ci-failure-digest, pr-auto-labeler, pr-size-check, stale-cleanup, weekly-cad-sweep. Good automation but no multi-version matrix. |
| I: Code Style | 7/10 | Consistent use of frozen dataclasses. from __future__ import annotations. Type aliases defined (FloatArray, IntArray). Some inconsistency in property delegation patterns (MaterialLayer wraps every field individually). |
| J: API Design | 7/10 | VesselDrafterLayout as frozen dataclass provides clean configuration interface. build_vessel_drafter_components() is the main entry point. Preview/scene split is clean. Some GUI callbacks could be better typed. |
| K: Data Handling | 8/10 | Engineering units consistently used (inches, degrees). MM_PER_INCH conversion constant. MaterialProperties with density, thermal conductivity, expansion coefficients. Vessel profiles computed from parametric curves. |
| L: Logging | 5/10 | 3 print statements remain. No logging module usage visible in sampled files. Should use logging for CAD export progress and error reporting. |
| M: Configuration | 7/10 | DEFAULT_VESSEL_DRAFTER_LAYOUT provides sensible defaults. Profiles configurable via vessel_drafter_profiles.py. View options in Vessel3DViewOptions dataclass. |
| N: Scalability | 7/10 | Adding new vessel types requires new model + layout + profile modules. Scene mesh generation scales with angular segment count. Export pipeline is extensible (STEP, DXF). |

**Overall: 6.9/10**

## Key Findings

### DRY
- contracts.py centralizes validation functions, avoiding scattered checks
- vessel_drafter_scene.py reuses build functions from projects/ and preview/ modules
- MaterialLayer delegates all properties to MaterialProperties, which is good composition but creates verbose wrapper code -- could use __getattr__ delegation instead
- Profile generation (build_top_head_curve, build_bottom_head_curve, build_shell_band_profiles) properly factored into reusable builders

### DbC
- 18 DbC patterns, concentrated in contracts.py with 6 guard functions
- require_positive, require_nonnegative, require_fraction, require_integer_at_least, require_less_or_equal, require_finite cover the primary validation needs
- VesselDrafterLayout likely validates via __post_init__ using these guards
- Weaker contract enforcement in GUI and preview modules

### TDD
- Test-to-source ratio of 0.32 (9/28) is below ideal
- Tests cover core domain (geometry, defaults, metrics) and export
- GUI tests exist (test_vessel_drafter_gui.py) which is commendable
- Missing tests for cli.py, vessel_materials.py, and some layout modules
- No property-based or fuzz testing

### LOD
- Clean separation: preview modules call build_vessel_drafter_components() rather than manipulating geometry directly
- MaterialLayer wraps MaterialProperties through delegated properties rather than exposing the inner object
- GUI modules access model data through the layout/components interface
- Some potential violations in vessel_drafter_scene.py which accesses nested profile point attributes

## Issues to Create
| Issue | Title | Priority |
|-------|-------|----------|
| 1 | Add tests for cli.py and vessel_materials.py (improve coverage from 0.32 to 0.50+) | High |
| 2 | Replace 3 print statements with logging calls | Medium |
| 3 | Split vessel_drafter_scene.py (739 LOC) into mesh generation and scene assembly modules | Medium |
| 4 | Add bandit security scan to CI pipeline | Medium |
| 5 | Simplify MaterialLayer property delegation using __getattr__ | Low |
| 6 | Add CLAUDE.md for project-level development context | Low |
