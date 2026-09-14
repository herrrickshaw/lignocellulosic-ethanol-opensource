import pytest

from lignocellulosic_ethanol import enzymatic_hydrolysis as EH
from lignocellulosic_ethanol import feedstock as F
from lignocellulosic_ethanol import pretreatment as PT


def test_glucose_mass_gain_matches_exact_molecular_weight_ratio():
    fs = F.corn_stover(1000.0)
    pt = PT.pretreat(fs)
    r = EH.hydrolyze_cellulose(pt, cellulose_conversion_efficiency=1.0)
    expected = pt.cellulose_passthrough_kg_s * (180.156 / 162.14)
    assert r.glucose_produced_kg_s == pytest.approx(expected, rel=1e-9)


def test_cellulose_to_glucose_ratio_matches_starch_to_glucose_ratio():
    # Cellulose and starch are both glucose polymers -- same exact MW ratio.
    assert EH.CELLULOSE_TO_GLUCOSE_MW_RATIO == pytest.approx(180.156 / 162.14, rel=1e-9)


@pytest.mark.parametrize("preset,expected_range", [
    (F.rice_straw, (13.0, 15.0)),      # high ash -> below the cited real residue range
    (F.corn_stover, (16.3, 19.8)),     # inside the cited real range (7,000-8,500 BTU/lb)
    (F.bagasse, (21.0, 24.0)),         # high lignin -> above the cited real residue range
])
def test_lignin_residue_hhv_matches_expected_zone_per_feedstock(preset, expected_range):
    fs = preset(1000.0)
    pt = PT.pretreat(fs)
    hy = EH.hydrolyze_cellulose(pt)
    result = EH.lignin_residue_energy(pt, hy, fs)
    lo, hi = expected_range
    assert lo < result.blended_hhv_MJ_kg < hi


def test_rejects_efficiency_outside_zero_to_one():
    fs = F.rice_straw(1000.0)
    pt = PT.pretreat(fs)
    with pytest.raises(ValueError):
        EH.hydrolyze_cellulose(pt, cellulose_conversion_efficiency=1.5)
