import pytest

from lignocellulosic_ethanol import cofermentation as CF
from lignocellulosic_ethanol import enzymatic_hydrolysis as EH
from lignocellulosic_ethanol import feedstock as F
from lignocellulosic_ethanol import pretreatment as PT


def test_glucose_and_xylose_theoretical_yields_are_identical():
    # The elegant, derived (not asserted) fact this module's docstring explains:
    # both are (CH2O)n carbohydrates, so the mass yield per kg sugar is the same.
    assert CF.THEORETICAL_ETHANOL_YIELD_FROM_GLUCOSE_KG_PER_KG == pytest.approx(
        CF.THEORETICAL_ETHANOL_YIELD_FROM_XYLOSE_KG_PER_KG, rel=1e-9)
    assert CF.THEORETICAL_ETHANOL_YIELD_FROM_GLUCOSE_KG_PER_KG == pytest.approx(0.5114, abs=1e-3)


def test_coferment_combines_both_sugar_streams():
    fs = F.rice_straw(1000.0)
    pt = PT.pretreat(fs)
    hy = EH.hydrolyze_cellulose(pt)
    r = CF.coferment(hy, pt)
    assert r.total_ethanol_kg_s == pytest.approx(r.ethanol_from_glucose_kg_s + r.ethanol_from_xylose_kg_s)
    assert r.ethanol_from_glucose_kg_s > 0
    assert r.ethanol_from_xylose_kg_s > 0


def test_zero_xylose_efficiency_means_all_ethanol_from_glucose():
    fs = F.rice_straw(1000.0)
    pt = PT.pretreat(fs)
    hy = EH.hydrolyze_cellulose(pt)
    r = CF.coferment(hy, pt, xylose_fermentation_efficiency=1e-9)
    assert r.ethanol_from_xylose_kg_s == pytest.approx(0.0, abs=1e-6)
    assert r.total_ethanol_kg_s == pytest.approx(r.ethanol_from_glucose_kg_s, rel=1e-6)


def test_rejects_efficiencies_outside_zero_to_one():
    fs = F.rice_straw(1000.0)
    pt = PT.pretreat(fs)
    hy = EH.hydrolyze_cellulose(pt)
    with pytest.raises(ValueError):
        CF.coferment(hy, pt, glucose_fermentation_efficiency=1.5)
    with pytest.raises(ValueError):
        CF.coferment(hy, pt, xylose_fermentation_efficiency=0.0)
