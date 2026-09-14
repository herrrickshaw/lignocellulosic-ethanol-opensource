"""Dilute-acid pretreatment: hydrolyses the hemicellulose fraction to its
monomer sugar, xylose, opening up the cellulose fraction for the
downstream enzymatic hydrolysis step (`enzymatic_hydrolysis.py`) --
standard first unit operation in a 2G cellulosic-ethanol process
(reviewed across the dilute-acid pretreatment literature this module
cites in docs/METHODOLOGY.md).

Hemicellulose (approximated here as a xylan polymer, (C5H8O4)n) hydrolyses
via n H2O addition to n xylose monomers, C5H10O5 -- an exact
stoichiometric mass gain of MW(xylose)/MW(xylan monomer) = 150.13/132.12
= 1.1363 (both real molecular weights, derived here rather than quoted,
the same "derive, don't recall" choice the ethanol-design-opensource
sibling repo makes for `feedstock.py`'s starch-to-glucose factor).

Real xylose recovery is well below 100% -- published dilute-acid studies
report a wide range (55-85%) depending on severity (time, temperature,
acid concentration): 84% at 130 C/30 min/0.125 g acid per g biomass;
85% at 140 C/2.5 h with oxalic acid; 55-59% for one sugarcane-biomass
study. This module takes `xylose_recovery_fraction` as a direct,
overridable input (default 0.75, the approximate midpoint of the cited
range) rather than deriving it from a combined-severity-factor formula
-- the several published severity-factor formulations differ in exact
form across sources, and misquoting one from memory would be a real
transcription risk this project avoids elsewhere by preferring a cited,
overridable input over an internally reconstructed formula it cannot
independently verify.

This module assumes cellulose is NOT significantly solubilized during
dilute-acid pretreatment (a standard simplification -- dilute acid
targets hemicellulose specifically, leaving cellulose largely intact
but more enzyme-accessible, per the same pretreatment literature) -- it
passes through unchanged to `enzymatic_hydrolysis.py`."""
from __future__ import annotations

from dataclasses import dataclass

from .feedstock import LignocellulosicFeedstock

XYLAN_TO_XYLOSE_MW_RATIO = 150.13 / 132.12  # exact MW ratio, derived not quoted
DEFAULT_XYLOSE_RECOVERY_FRACTION = 0.75


@dataclass
class PretreatmentResult:
    feedstock_name: str
    xylose_produced_kg_s: float
    cellulose_passthrough_kg_s: float
    lignin_passthrough_kg_s: float
    unrecovered_hemicellulose_kg_s: float
    xylose_recovery_fraction: float


def pretreat(feedstock: LignocellulosicFeedstock,
            xylose_recovery_fraction: float = DEFAULT_XYLOSE_RECOVERY_FRACTION) -> PretreatmentResult:
    if not 0 < xylose_recovery_fraction <= 1.0:
        raise ValueError("xylose_recovery_fraction must be in (0, 1]")

    hemicellulose_kg_s = feedstock.hemicellulose_kg_s()
    xylose_kg_s = hemicellulose_kg_s * XYLAN_TO_XYLOSE_MW_RATIO * xylose_recovery_fraction
    # Mass of hemicellulose that did NOT convert to recovered xylose (lost to degradation
    # products -- furfural etc. -- or left unreacted in the solid), on the ORIGINAL
    # (pre-hydrolysis) polymer mass basis, not the xylose-monomer basis.
    unrecovered_hemicellulose_kg_s = hemicellulose_kg_s * (1 - xylose_recovery_fraction)

    return PretreatmentResult(
        feedstock_name=feedstock.name,
        xylose_produced_kg_s=xylose_kg_s,
        cellulose_passthrough_kg_s=feedstock.cellulose_kg_s(),
        lignin_passthrough_kg_s=feedstock.lignin_kg_s(),
        unrecovered_hemicellulose_kg_s=unrecovered_hemicellulose_kg_s,
        xylose_recovery_fraction=xylose_recovery_fraction,
    )
