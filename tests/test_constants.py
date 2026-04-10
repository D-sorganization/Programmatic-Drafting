from pathlib import Path

from programmatic_drafting.constants import MM_PER_INCH


def test_mm_per_inch_is_shared_across_drafting_models() -> None:
    root = Path(__file__).resolve().parents[1]
    bath_source = (
        root / "src/programmatic_drafting/models/cylindrical_bath.py"
    ).read_text()
    vessel_source = (
        root / "src/programmatic_drafting/models/vessel_drafter.py"
    ).read_text()

    assert MM_PER_INCH == 25.4
    assert "MM_PER_INCH = 25.4" not in bath_source
    assert "MM_PER_INCH = 25.4" not in vessel_source
    assert "from programmatic_drafting.constants import MM_PER_INCH" in bath_source
    assert "from programmatic_drafting.constants import MM_PER_INCH" in vessel_source
