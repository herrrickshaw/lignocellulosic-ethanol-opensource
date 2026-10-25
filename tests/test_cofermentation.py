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


# --- Cross-check against the NREL design case (Humbird et al. 2011, NREL/TP-5100-47764).
# Hand-computed from molecular weights, not from the module's constants:
#   glucan->glucose 180.156/162.14, xylan->xylose 150.13/132.12,
#   ethanol per sugar 2*46.068/180.156 = (5/3)*46.068/150.13 = 0.51143 kg/kg.
# Humbird corn stover: glucan 35.05 %, xylan 19.53 % (dry). Conversion targets:
#   pretreatment xylan->xylose 90 %, enzymatic glucan->glucose 90 %,
#   fermentation glucose->EtOH 95 %, xylose->EtOH 85 %.
# Humbird's reported yield is 79.0 gal / dry US ton = 79.0*3.78541/0.907185 = 329.6 L/t,
# which also counts arabinose/galactose/mannose and subtracts contamination losses,
# so glucan+xylan alone should land within a few percent of it.

_Y = 2 * 46.068 / 180.156
_HUMBIRD_L_PER_DRY_T = 79.0 * 3.78541 / 0.907185


def _chain_L_per_t(fs, xr, cc, ge, xe):
    pt = PT.pretreat(fs, xylose_recovery_fraction=xr)
    hy = EH.hydrolyze_cellulose(pt, cellulose_conversion_efficiency=cc)
    r = CF.coferment(hy, pt, glucose_fermentation_efficiency=ge, xylose_fermentation_efficiency=xe)
    return r.total_ethanol_l_s / fs.mass_flow_kg_s * 1000.0


def test_humbird_targets_reproduce_hand_computed_yield():
    fs = F.LignocellulosicFeedstock("Humbird 2011 corn stover", 1.0, 0.3505, 0.1953, 0.1576, 0.0493)
    expected_kg = (0.3505 * 180.156 / 162.14 * 0.90 * _Y * 0.95
                   + 0.1953 * 150.13 / 132.12 * 0.90 * _Y * 0.85)
    assert _chain_L_per_t(fs, 0.90, 0.90, 0.95, 0.85) == pytest.approx(expected_kg / 0.789 * 1000, rel=1e-4)


def test_humbird_targets_land_within_3pct_of_nrel_design_yield():
    fs = F.LignocellulosicFeedstock("Humbird 2011 corn stover", 1.0, 0.3505, 0.1953, 0.1576, 0.0493)
    assert _chain_L_per_t(fs, 0.90, 0.90, 0.95, 0.85) == pytest.approx(_HUMBIRD_L_PER_DRY_T, rel=0.03)


def test_default_midpoint_yields_sit_about_17pct_below_the_nrel_design_case():
    # Documents (does not endorse) the repo's literature-midpoint defaults:
    # 0.36*1.1111*0.75*0.51143*0.90 + 0.21*1.1363*0.75*0.51143*0.85 = 0.21589 kg/kg -> 273.6 L/t
    got = _chain_L_per_t(F.corn_stover(1.0), PT.DEFAULT_XYLOSE_RECOVERY_FRACTION,
                         EH.DEFAULT_CELLULOSE_CONVERSION_EFFICIENCY,
                         CF.DEFAULT_GLUCOSE_FERMENTATION_EFFICIENCY, CF.DEFAULT_XYLOSE_FERMENTATION_EFFICIENCY)
    assert got == pytest.approx(273.6, abs=0.2)
    assert got / _HUMBIRD_L_PER_DRY_T == pytest.approx(0.83, abs=0.01)
