import math

import pytest

from lignocellulosic_ethanol import distillation as D


def test_gilliland_reproduces_its_own_two_limiting_cases():
    n_min, r_min = 8.0, 10.0
    # R -> Rmin: infinite stages (the classic pinch-point limit)
    n_near_rmin = D.gilliland_stages(n_min, r_min, r_min * 1.0001)
    assert n_near_rmin > 100
    # R -> infinity: total reflux, N -> Nmin
    n_huge_r = D.gilliland_stages(n_min, r_min, r_min * 1000)
    assert n_huge_r == pytest.approx(n_min, rel=0.01)


def test_gilliland_rejects_reflux_at_or_below_minimum():
    with pytest.raises(ValueError):
        D.gilliland_stages(8.0, 10.0, 9.5)


def test_relative_volatility_exceeds_one_below_the_azeotrope():
    alpha = D.relative_volatility_avg(x_bottoms_mole=0.001, x_distillate_mole=0.70)
    assert alpha > 1.0


def test_design_column_gives_a_plausible_stage_count_for_a_typical_wash():
    # A typical fermented wash (~8 wt% ethanol) distilled up toward the azeotrope --
    # real industrial beer/rectifier columns commonly run in the 15-30 actual-stage
    # range for this duty (a plausibility check, not a precision-matched benchmark).
    r = D.design_column(x_feed_mass_frac=0.08, x_distillate_mass_frac=0.93, x_bottoms_mass_frac=0.0005)
    assert 5 < r.n_actual_stages < 40
    assert r.r_actual > r.r_min > 0
    assert r.n_actual_stages > r.n_min_stages


def test_design_column_rejects_out_of_order_compositions():
    with pytest.raises(ValueError):
        D.design_column(x_feed_mass_frac=0.50, x_distillate_mass_frac=0.30, x_bottoms_mass_frac=0.001)


def test_richer_distillate_target_needs_more_stages():
    lean = D.design_column(x_feed_mass_frac=0.08, x_distillate_mass_frac=0.85, x_bottoms_mass_frac=0.0005)
    rich = D.design_column(x_feed_mass_frac=0.08, x_distillate_mass_frac=0.94, x_bottoms_mass_frac=0.0005)
    assert rich.n_actual_stages > lean.n_actual_stages


def test_fenske_hand_computed_constant_alpha():
    # ln[(0.8/0.2)*(0.99/0.01)] / ln 2 = ln 396 / ln 2 = 8.6294
    assert D.fenske_min_stages(0.8, 0.01, 2.0) == pytest.approx(8.6294, abs=1e-4)


def test_minimum_reflux_hand_computed():
    # alpha 2, xF 0.1: y* = 0.2/1.1 = 0.181818; Rmin = (0.8-0.181818)/(0.181818-0.1) = 7.5556
    assert D.minimum_reflux_saturated_liquid_feed(0.1, 0.8, 2.0) == pytest.approx(7.5556, abs=1e-4)


def test_minimum_reflux_rejects_alpha_at_or_below_one():
    with pytest.raises(ValueError):
        D.minimum_reflux_saturated_liquid_feed(0.5, 0.8, 1.0)
