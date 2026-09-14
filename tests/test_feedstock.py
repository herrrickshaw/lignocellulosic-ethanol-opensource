import pytest

from lignocellulosic_ethanol import feedstock as F


def test_presets_have_plausible_compositions_summing_under_one():
    for preset in (F.rice_straw, F.corn_stover, F.bagasse):
        fs = preset(1000.0)
        total = fs.cellulose_mass_frac + fs.hemicellulose_mass_frac + fs.lignin_mass_frac + fs.ash_mass_frac
        assert 0 < total <= 1.0


def test_rice_straw_has_distinctively_high_ash():
    rs, cs, bg = F.rice_straw(1000.0), F.corn_stover(1000.0), F.bagasse(1000.0)
    assert rs.ash_mass_frac > cs.ash_mass_frac
    assert rs.ash_mass_frac > bg.ash_mass_frac


def test_bagasse_has_distinctively_high_lignin():
    rs, cs, bg = F.rice_straw(1000.0), F.corn_stover(1000.0), F.bagasse(1000.0)
    assert bg.lignin_mass_frac > rs.lignin_mass_frac
    assert bg.lignin_mass_frac > cs.lignin_mass_frac


def test_component_flows_scale_with_mass_flow():
    fs = F.rice_straw(500.0)
    assert fs.cellulose_kg_s() == pytest.approx(500.0 * fs.cellulose_mass_frac)


def test_rejects_fractions_exceeding_one():
    with pytest.raises(ValueError):
        F.LignocellulosicFeedstock("bad", 1000.0, 0.5, 0.4, 0.3, 0.2)
