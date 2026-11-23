"""Hand-computed values, boundaries and error paths for the lignocellulosic ethanol modules.

Expected numbers are derived on paper from the formulas in the module
docstrings. CoolProp is only used at 1 atm (the shipped default).
"""
import math

import pytest

from lignocellulosic_ethanol import cofermentation as CF
from lignocellulosic_ethanol import dehydration as DH
from lignocellulosic_ethanol import distillation as D
from lignocellulosic_ethanol import enzymatic_hydrolysis as EH
from lignocellulosic_ethanol import feedstock as F
from lignocellulosic_ethanol import pretreatment as PT
from lignocellulosic_ethanol import properties as P

# ---------------------------------------------------------------- feedstock


def test_presets_expose_cited_fractions_and_flows():
    r = F.rice_straw(10.0)
    assert (r.name, r.mass_flow_kg_s) == ("rice straw", 10.0)
    assert r.cellulose_kg_s() == pytest.approx(3.5)
    assert r.hemicellulose_kg_s() == pytest.approx(2.0)
    assert r.lignin_kg_s() == pytest.approx(1.3)
    assert r.ash_kg_s() == pytest.approx(1.5)
    c = F.corn_stover(10.0)
    assert (c.cellulose_mass_frac, c.hemicellulose_mass_frac, c.lignin_mass_frac, c.ash_mass_frac) == (
        0.36, 0.21, 0.178, 0.07)
    b = F.bagasse(10.0)
    assert b.lignin_mass_frac == 0.3036 and b.name == "sugarcane bagasse"
    assert set(F.FEEDSTOCKS) == {"Rice straw", "Corn stover", "Bagasse"}
    assert F.FEEDSTOCKS["Bagasse"](2.0).mass_flow_kg_s == 2.0


def test_every_preset_leaves_a_remainder_below_one():
    for fn in F.FEEDSTOCKS.values():
        f = fn(1.0)
        total = f.cellulose_mass_frac + f.hemicellulose_mass_frac + f.lignin_mass_frac + f.ash_mass_frac
        assert 0.8 < total < 1.0


def test_feedstock_fraction_total_must_be_in_zero_exclusive_one_inclusive():
    F.LignocellulosicFeedstock("full", 1.0, 0.5, 0.25, 0.15, 0.10)    # exactly 1.0 is allowed
    with pytest.raises(ValueError, match="in \\(0, 1\\]"):
        F.LignocellulosicFeedstock("over", 1.0, 0.5, 0.25, 0.15, 0.11)
    with pytest.raises(ValueError):
        F.LignocellulosicFeedstock("empty", 1.0, 0.0, 0.0, 0.0, 0.0)
    with pytest.raises(ValueError):
        F.LignocellulosicFeedstock("negative", 1.0, -0.1, 0.0, 0.0, 0.0)


# ------------------------------------------------------------- pretreatment


def test_pretreatment_hand_computed():
    f = F.rice_straw(10.0)   # hemicellulose 2.0 kg/s
    r = PT.pretreat(f)       # default recovery 0.75
    assert r.xylose_produced_kg_s == pytest.approx(2.0 * (150.13 / 132.12) * 0.75)
    assert r.unrecovered_hemicellulose_kg_s == pytest.approx(0.5)
    assert r.cellulose_passthrough_kg_s == pytest.approx(3.5)
    assert r.lignin_passthrough_kg_s == pytest.approx(1.3)
    assert r.xylose_recovery_fraction == 0.75 and r.feedstock_name == "rice straw"
    full = PT.pretreat(f, 1.0)
    assert full.unrecovered_hemicellulose_kg_s == 0.0
    assert full.xylose_produced_kg_s == pytest.approx(2.0 * 150.13 / 132.12)
    assert full.xylose_produced_kg_s > 2.0  # hydrolysis adds water mass


@pytest.mark.parametrize("bad", [0.0, -0.1, 1.0001])
def test_pretreatment_recovery_range(bad):
    with pytest.raises(ValueError, match="xylose_recovery_fraction"):
        PT.pretreat(F.rice_straw(1.0), bad)


# ----------------------------------------------------- enzymatic hydrolysis


def test_hydrolysis_hand_computed():
    pre = PT.pretreat(F.rice_straw(10.0))   # cellulose 3.5 kg/s
    h = EH.hydrolyze_cellulose(pre)
    assert h.glucose_produced_kg_s == pytest.approx(3.5 * 180.156 / 162.14 * 0.75)
    assert h.unconverted_cellulose_kg_s == pytest.approx(0.875)
    assert h.cellulose_conversion_efficiency == 0.75
    full = EH.hydrolyze_cellulose(pre, 1.0)
    assert full.unconverted_cellulose_kg_s == 0.0
    # carbon-bearing mass is conserved apart from the added water: glucose + unconverted > cellulose
    assert h.glucose_produced_kg_s + h.unconverted_cellulose_kg_s > 3.5


@pytest.mark.parametrize("bad", [0.0, -0.5, 1.0001])
def test_hydrolysis_efficiency_range(bad):
    with pytest.raises(ValueError, match="cellulose_conversion_efficiency"):
        EH.hydrolyze_cellulose(PT.pretreat(F.rice_straw(1.0)), bad)


def test_lignin_residue_hand_computed_for_rice_straw():
    f = F.rice_straw(10.0)
    pre = PT.pretreat(f)
    hyd = EH.hydrolyze_cellulose(pre)
    res = EH.lignin_residue_energy(pre, hyd, f)
    # lignin 1.3 + ash 1.5 + carbohydrate (0.5 hemi + 0.875 cellulose) = 4.175 kg/s
    assert res.residue_mass_flow_kg_s == pytest.approx(4.175)
    # (1.3*26.7 + 1.375*17.5) / 4.175 = 14.077 MJ/kg  (docstring: rice straw ~14.1)
    assert res.blended_hhv_MJ_kg == pytest.approx((1.3 * 26.7 + 1.375 * 17.5) / 4.175)
    assert res.blended_hhv_MJ_kg == pytest.approx(14.08, abs=0.01)


def test_lignin_residue_hhv_is_between_carbohydrate_and_lignin_when_ash_free():
    f = F.LignocellulosicFeedstock("ash-free", 10.0, 0.4, 0.2, 0.4, 0.0)
    pre = PT.pretreat(f)
    res = EH.lignin_residue_energy(pre, EH.hydrolyze_cellulose(pre), f)
    assert 17.5 < res.blended_hhv_MJ_kg < 26.7


def test_lignin_residue_rejects_an_empty_residue():
    f = F.LignocellulosicFeedstock("pure cellulose", 1.0, 0.5, 0.0, 0.0, 0.0)
    pre = PT.pretreat(f)
    with pytest.raises(ValueError, match="non-positive"):
        EH.lignin_residue_energy(pre, EH.hydrolyze_cellulose(pre, 1.0), f)


# --------------------------------------------------------- co-fermentation


def test_theoretical_ethanol_yields_from_each_sugar_agree():
    assert CF.THEORETICAL_ETHANOL_YIELD_FROM_GLUCOSE_KG_PER_KG == pytest.approx(0.51144, abs=1e-4)
    assert CF.THEORETICAL_ETHANOL_YIELD_FROM_XYLOSE_KG_PER_KG == pytest.approx(0.51139, abs=1e-4)
    assert CF.THEORETICAL_ETHANOL_YIELD_FROM_XYLOSE_KG_PER_KG == pytest.approx(
        CF.THEORETICAL_ETHANOL_YIELD_FROM_GLUCOSE_KG_PER_KG, rel=1e-3)


def _streams(glucose, xylose):
    pre = PT.PretreatmentResult("x", xylose, 0.0, 0.0, 0.0, 1.0)
    hyd = EH.HydrolysisResult(glucose, 0.0, 1.0)
    return hyd, pre


def test_coferment_hand_computed_at_full_efficiency():
    hyd, pre = _streams(10.0, 10.0)
    r = CF.coferment(hyd, pre, 1.0, 1.0)
    assert r.ethanol_from_glucose_kg_s == pytest.approx(10.0 * 2 * 46.068 / 180.156)
    assert r.ethanol_from_xylose_kg_s == pytest.approx(10.0 * (5.0 / 3.0) * 46.068 / 150.13)
    assert r.total_ethanol_kg_s == pytest.approx(r.ethanol_from_glucose_kg_s + r.ethanol_from_xylose_kg_s)
    assert r.total_ethanol_l_s == pytest.approx(r.total_ethanol_kg_s / 0.789)


def test_coferment_default_efficiencies_apply_to_the_right_sugar():
    hyd, pre = _streams(10.0, 10.0)
    full = CF.coferment(hyd, pre, 1.0, 1.0)
    d = CF.coferment(hyd, pre)
    assert (d.glucose_fermentation_efficiency, d.xylose_fermentation_efficiency) == (0.90, 0.85)
    assert d.ethanol_from_glucose_kg_s == pytest.approx(0.90 * full.ethanol_from_glucose_kg_s)
    assert d.ethanol_from_xylose_kg_s == pytest.approx(0.85 * full.ethanol_from_xylose_kg_s)


def test_coferment_with_only_one_sugar():
    hyd, pre = _streams(10.0, 0.0)
    r = CF.coferment(hyd, pre)
    assert r.ethanol_from_xylose_kg_s == 0.0
    assert r.total_ethanol_kg_s == r.ethanol_from_glucose_kg_s


def test_coferment_efficiency_ranges_are_checked_per_sugar():
    hyd, pre = _streams(1.0, 1.0)
    for bad in (0.0, -0.1, 1.0001):
        with pytest.raises(ValueError, match="glucose_fermentation_efficiency"):
            CF.coferment(hyd, pre, glucose_fermentation_efficiency=bad)
        with pytest.raises(ValueError, match="xylose_fermentation_efficiency"):
            CF.coferment(hyd, pre, xylose_fermentation_efficiency=bad)
    assert CF.coferment(hyd, pre, 1.0, 1.0).glucose_fermentation_efficiency == 1.0


# --------------------------------------------------------------- properties


def test_mass_mole_fraction_conversions():
    assert P.mole_frac_to_mass_frac_ethanol(0.0) == 0.0
    assert P.mole_frac_to_mass_frac_ethanol(1.0) == pytest.approx(1.0)
    # x = 0.5 -> 46.068 / (46.068 + 18.015)
    assert P.mole_frac_to_mass_frac_ethanol(0.5) == pytest.approx(46.068 / (46.068 + 18.015), abs=1e-4)
    assert P.mass_frac_to_mole_frac_ethanol(0.0) == 0.0
    for w in (0.01, 0.2, 0.5, 0.956):
        assert P.mole_frac_to_mass_frac_ethanol(P.mass_frac_to_mole_frac_ethanol(w)) == pytest.approx(w)
    # ethanol is heavier per mole, so mass fraction exceeds mole fraction
    assert P.mole_frac_to_mass_frac_ethanol(0.3) > 0.3


@pytest.mark.parametrize("x", [0.0, 1.0, -0.1, 1.1])
def test_bubble_point_rejects_x_outside_open_unit_interval(x):
    with pytest.raises(ValueError):
        P.bubble_point(x)


def test_bubble_point_physical_invariants_at_one_atm():
    pt = P.bubble_point(0.10)
    assert pt.x_ethanol_mole == 0.10
    assert 351.0 < pt.T_K < 373.15           # between ethanol and water normal boiling points
    assert pt.y_ethanol_mole > 0.10          # dilute ethanol enriches in the vapour
    assert pt.relative_volatility > 1.0
    x, y = pt.x_ethanol_mole, pt.y_ethanol_mole
    assert pt.relative_volatility == pytest.approx((y / (1 - y)) / (x / (1 - x)))
    assert P.bubble_point(0.5).T_K < pt.T_K  # more ethanol -> lower boiling point


def test_find_azeotrope_reports_a_point_where_y_equals_x():
    az = P.find_azeotrope()
    assert az.y_ethanol_mole == pytest.approx(az.x_ethanol_mole, abs=2e-3)
    assert 0.85 < az.x_ethanol_mole < 0.93
    assert 350.0 < az.T_K < 352.0


def test_find_azeotrope_raises_when_not_bracketed():
    with pytest.raises(ValueError, match="not bracketed"):
        P.find_azeotrope(lo=0.10, hi=0.50)


def test_find_azeotrope_respects_max_iter():
    coarse = P.find_azeotrope(max_iter=1)
    fine = P.find_azeotrope()
    # one bisection step leaves a much wider bracket than the converged answer
    assert abs(coarse.x_ethanol_mole - fine.x_ethanol_mole) > 1e-3


# ------------------------------------------------------------- distillation


def test_fenske_hand_computed():
    # ln[(0.9/0.1) * (0.9/0.1)] / ln 3 = ln 81 / ln 3 = 4
    assert D.fenske_min_stages(0.9, 0.1, 3.0) == pytest.approx(4.0)
    assert D.fenske_min_stages(0.99, 0.1, 3.0) > D.fenske_min_stages(0.9, 0.1, 3.0)
    assert D.fenske_min_stages(0.9, 0.1, 6.0) < D.fenske_min_stages(0.9, 0.1, 3.0)


def test_saturated_liquid_feed_rmin_hand_computed():
    # alpha=2, xF=0.2 -> y_eq = 0.4/1.2 = 1/3 ; Rmin = (0.8 - 1/3) / (1/3 - 0.2) = 3.5
    assert D.minimum_reflux_saturated_liquid_feed(0.2, 0.8, 2.0) == pytest.approx(3.5)


@pytest.mark.parametrize("alpha", [1.0, 0.8])
def test_saturated_liquid_feed_rmin_needs_alpha_above_one(alpha):
    with pytest.raises(ValueError, match="above the feed"):
        D.minimum_reflux_saturated_liquid_feed(0.2, 0.8, alpha)


def test_gilliland_hand_computed_point():
    # R=1.5, Rmin=1: X = 0.5/2.5 = 0.2; Molokanov Y = 0.46056; N = (4 + Y)/(1 - Y)
    assert D.gilliland_stages(4.0, 1.0, 1.5) == pytest.approx(8.2693, rel=1e-3)


def test_gilliland_more_reflux_means_fewer_stages_and_never_below_nmin():
    stages = [D.gilliland_stages(6.0, 2.0, r) for r in (2.2, 3.0, 5.0, 20.0)]
    assert stages == sorted(stages, reverse=True)
    assert all(n > 6.0 for n in stages)


def test_gilliland_equal_reflux_is_rejected():
    with pytest.raises(ValueError, match="must exceed"):
        D.gilliland_stages(8.0, 10.0, 10.0)


def test_relative_volatility_avg_is_the_geometric_mean_of_end_alphas():
    a_bot = P.bubble_point(0.01).relative_volatility
    a_top = P.bubble_point(0.5).relative_volatility
    assert D.relative_volatility_avg(0.01, 0.5) == pytest.approx(math.sqrt(a_bot * a_top))
    assert a_top < a_bot


def test_design_column_rejects_misordered_compositions():
    with pytest.raises(ValueError, match="x_bottoms < x_feed < x_distillate"):
        D.design_column(0.93, 0.08, 0.0005)
    with pytest.raises(ValueError):
        D.design_column(0.08, 0.93, 0.08)      # bottoms == feed
    with pytest.raises(ValueError):
        D.design_column(0.5, 0.5, 0.001)       # feed == distillate
    with pytest.raises(ValueError):
        D.design_column(0.0001, 0.93, 0.0005)  # feed leaner than bottoms


def test_design_column_reflux_factor_and_consistency():
    base = D.design_column(0.08, 0.90, 0.0005)
    assert D.DEFAULT_REFLUX_RATIO_FACTOR == 1.3
    assert base.r_actual == pytest.approx(1.3 * base.r_min)
    assert base.r_min == pytest.approx(D.minimum_reflux_saturated_liquid_feed(
        base.x_feed_mole, base.x_distillate_mole, base.relative_volatility_avg))
    tight = D.design_column(0.08, 0.90, 0.0005, reflux_ratio_factor=2.0)
    assert tight.r_actual == pytest.approx(2.0 * tight.r_min)
    assert tight.n_actual_stages < base.n_actual_stages
    assert base.n_actual_stages > base.n_min_stages
    assert base.distillate_mass_frac_ethanol == pytest.approx(0.90)
    assert base.x_distillate_mole == pytest.approx(P.mass_frac_to_mole_frac_ethanol(0.90))
    assert base.x_bottoms_mole < base.x_feed_mole < base.x_distillate_mole


# ------------------------------------------------------------ dehydration

_M, _W = 1.9, 0.045
# paper sizing: water = 1.9*3600*8*0.045 ; mass = water/0.04 ; V = mass/700
_WATER = _M * 3600 * 8 * _W
_AREA = (_M / 1.5) / 0.30
_VOL = _WATER / 0.04 / 700.0
_HEIGHT = _VOL / _AREA
_DIAM = math.sqrt(4 * _AREA / math.pi)


def test_bed_geometry_hand_computed():
    r = DH.size_dehydration_bed(_M, _W)
    assert r.water_removed_per_cycle_kg == pytest.approx(2462.4)
    assert r.bed_mass_kg == pytest.approx(61560.0)
    assert r.bed_volume_m3 == pytest.approx(61560.0 / 700.0)
    assert r.bed_diameter_m == pytest.approx(_DIAM)
    assert r.bed_height_m == pytest.approx(_HEIGHT)
    assert r.height_to_diameter_ratio == pytest.approx(_HEIGHT / _DIAM)
    assert r.regen_ethanol_vapor_flow_kg_s == pytest.approx(0.2 * _M)
    assert r.regen_latent_duty_kW == pytest.approx(2462.4 * 4.19 * 1000 / (4 * 3600))
    assert math.pi * (r.bed_diameter_m / 2) ** 2 * r.bed_height_m == pytest.approx(r.bed_volume_m3)


def test_parallel_vessel_flag_flips_at_aspect_ratio_eight():
    assert _HEIGHT / _DIAM > 8.0
    assert DH.size_dehydration_bed(_M, _W).recommend_parallel_vessels is True
    # a faster design velocity shrinks the area, so the same volume gets taller -> still flagged;
    # a slower one widens the bed and drops below 8:1
    wide = DH.size_dehydration_bed(_M, _W, design_velocity_m_s=0.20)
    assert wide.height_to_diameter_ratio < 8.0
    assert wide.recommend_parallel_vessels is False


def test_min_bed_height_guard_is_a_strict_less_than():
    DH.size_dehydration_bed(_M, _W, min_bed_height_m=_HEIGHT - 1e-6)
    with pytest.raises(ValueError, match="below the practical minimum"):
        DH.size_dehydration_bed(_M, _W, min_bed_height_m=_HEIGHT + 1e-6)


def test_inlet_water_range_is_exclusive_at_both_ends():
    for bad in (0.0, -0.01, 0.20, 0.25):
        with pytest.raises(ValueError, match="plausible"):
            DH.size_dehydration_bed(_M, bad)
    assert DH.size_dehydration_bed(_M, 0.199).water_removed_per_cycle_kg > 0


def test_bed_count_boundary_is_inclusive():
    two = DH.size_dehydration_bed(_M, _W, adsorption_time_h=8.0, regen_time_h=4.0, cooldown_time_h=4.0)
    three = DH.size_dehydration_bed(_M, _W, adsorption_time_h=8.0, regen_time_h=4.0, cooldown_time_h=4.01)
    assert two.n_beds == 2
    assert three.n_beds == 3


def test_bis_spec_flag_is_inclusive_at_the_limit():
    assert DH.size_dehydration_bed(_M, _W, outlet_water_vol_frac=0.008).meets_bis_spec is True
    assert DH.size_dehydration_bed(_M, _W, outlet_water_vol_frac=0.0081).meets_bis_spec is False


def test_sensible_duty_scales_with_purge_and_vanishes_at_zero_temperature_rise():
    base = DH.size_dehydration_bed(_M, _W)
    double = DH.size_dehydration_bed(_M, _W, regen_purge_fraction_of_feed=0.40)
    assert double.regen_sensible_duty_kW == pytest.approx(2 * base.regen_sensible_duty_kW)
    assert double.regen_latent_duty_kW == pytest.approx(base.regen_latent_duty_kW)  # latent is purge-independent
    flat = DH.size_dehydration_bed(_M, _W, feed_temperature_K=498.15, regen_temperature_C=225.0)
    assert flat.regen_sensible_duty_kW == pytest.approx(0.0, abs=1e-9)
    assert base.regen_sensible_duty_kW > 0


def test_working_capacity_and_bulk_density_drive_bed_mass_and_volume():
    r = DH.size_dehydration_bed(_M, _W, working_capacity_wt_pct=8.0, sieve_bulk_density_kg_m3=800.0,
                                min_bed_height_m=0.1)
    assert r.bed_mass_kg == pytest.approx(2462.4 / 0.08)
    assert r.bed_volume_m3 == pytest.approx(2462.4 / 0.08 / 800.0)


# ---------------------------------------------------- boundary / survivor tests


def test_regen_heater_duty_is_sum_of_the_two_components():
    r = DH.size_dehydration_bed(_M, _W)
    assert r.regen_heater_duty_kW == pytest.approx(r.regen_sensible_duty_kW + r.regen_latent_duty_kW)
    assert r.regen_heater_duty_kW > r.regen_latent_duty_kW


def test_bed_height_exactly_at_the_minimum_is_allowed():
    h = DH.size_dehydration_bed(_M, _W).bed_height_m
    assert DH.size_dehydration_bed(_M, _W, min_bed_height_m=h).bed_height_m == h


def test_parallel_vessel_threshold_constant():
    assert DH.MAX_SINGLE_VESSEL_ASPECT_RATIO == 8.0


def test_find_azeotrope_accepts_a_zero_at_the_bracket_end(monkeypatch):
    # (y - x) == 0 everywhere: the product f(lo)*f(hi) is exactly 0, which is not "no sign change"
    monkeypatch.setattr(P, "bubble_point", lambda x, P_Pa=101325.0: P.VLEPoint(x, x, 350.0, 1.0))
    az = P.find_azeotrope(lo=0.7, hi=0.99)
    assert 0.7 <= az.x_ethanol_mole <= 0.99
