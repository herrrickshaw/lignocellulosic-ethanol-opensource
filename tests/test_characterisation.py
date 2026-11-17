"""Characterisation tests: outputs of the pre-refactor code (tests/data/*)."""
from __future__ import annotations

import dataclasses
import json
import subprocess
import sys
from pathlib import Path

import pytest

from lignocellulosic_ethanol import cofermentation as CF
from lignocellulosic_ethanol import dehydration as DH
from lignocellulosic_ethanol import distillation as D
from lignocellulosic_ethanol import enzymatic_hydrolysis as EH
from lignocellulosic_ethanol import feedstock as F
from lignocellulosic_ethanol import pretreatment as PT
from lignocellulosic_ethanol import properties as P

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "tests" / "data"
GOLDEN = json.loads((DATA / "golden_baseline.json").read_text())


def _approx(expected, rel=1e-12):
    if isinstance(expected, dict):
        return {k: _approx(v, rel) for k, v in expected.items()}
    if isinstance(expected, float):
        return pytest.approx(expected, rel=rel)
    return expected


# The column/VLE design uses iterative searches whose last digits differ between platforms
# (macOS golden capture vs the Linux CI runner, ~1e-11 relative), so those use a looser bound.
ITERATIVE_REL = 1e-8


@pytest.mark.parametrize("name", ["rice_straw", "corn_stover", "bagasse"])
def test_chain_matches_baseline(name):
    feed = getattr(F, name)(4.927)
    pre = PT.pretreat(feed)
    hyd = EH.hydrolyze_cellulose(pre)
    got = {
        "feed": dataclasses.asdict(feed),
        "pre": dataclasses.asdict(pre),
        "hyd": dataclasses.asdict(hyd),
        "cof": dataclasses.asdict(CF.coferment(hyd, pre)),
        "res": dataclasses.asdict(EH.lignin_residue_energy(pre, hyd, feed)),
    }
    assert got == _approx(GOLDEN[name])


def test_column_bed_and_vle_match_baseline():
    assert dataclasses.asdict(D.design_column(0.03, 0.94, 0.0005)) == _approx(GOLDEN["column"], ITERATIVE_REL)
    assert dataclasses.asdict(DH.size_dehydration_bed(1.2, 0.06)) == _approx(GOLDEN["bed"], ITERATIVE_REL)
    assert dataclasses.asdict(P.find_azeotrope()) == _approx(GOLDEN["az"], ITERATIVE_REL)
    assert dataclasses.asdict(P.bubble_point(0.3)) == _approx(GOLDEN["bp"], ITERATIVE_REL)


def test_worked_example_stdout_unchanged():
    res = subprocess.run([sys.executable, str(ROOT / "examples" / "full_chain_worked_example.py")],
                         capture_output=True, text=True, check=True, cwd=ROOT)
    assert res.stdout == (DATA / "example_stdout.txt").read_text()
