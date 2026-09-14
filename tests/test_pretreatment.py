import pytest

from lignocellulosic_ethanol import feedstock as F
from lignocellulosic_ethanol import pretreatment as PT


def test_xylose_mass_gain_matches_exact_molecular_weight_ratio():
    fs = F.rice_straw(1000.0)
    r = PT.pretreat(fs, xylose_recovery_fraction=1.0)
    expected = fs.hemicellulose_kg_s() * (150.13 / 132.12)
    assert r.xylose_produced_kg_s == pytest.approx(expected, rel=1e-9)


def test_lower_recovery_gives_proportionally_less_xylose():
    fs = F.rice_straw(1000.0)
    full = PT.pretreat(fs, xylose_recovery_fraction=1.0)
    half = PT.pretreat(fs, xylose_recovery_fraction=0.5)
    assert half.xylose_produced_kg_s == pytest.approx(full.xylose_produced_kg_s * 0.5, rel=1e-9)


def test_cellulose_and_lignin_pass_through_unchanged():
    fs = F.corn_stover(1000.0)
    r = PT.pretreat(fs)
    assert r.cellulose_passthrough_kg_s == pytest.approx(fs.cellulose_kg_s())
    assert r.lignin_passthrough_kg_s == pytest.approx(fs.lignin_kg_s())


def test_unrecovered_hemicellulose_plus_xylose_basis_accounts_for_all_hemicellulose():
    fs = F.bagasse(1000.0)
    r = PT.pretreat(fs, xylose_recovery_fraction=0.75)
    # unrecovered_hemicellulose is on the original polymer mass basis
    assert r.unrecovered_hemicellulose_kg_s == pytest.approx(fs.hemicellulose_kg_s() * 0.25, rel=1e-9)


def test_rejects_recovery_outside_zero_to_one():
    fs = F.rice_straw(1000.0)
    with pytest.raises(ValueError):
        PT.pretreat(fs, xylose_recovery_fraction=1.5)
    with pytest.raises(ValueError):
        PT.pretreat(fs, xylose_recovery_fraction=0.0)
