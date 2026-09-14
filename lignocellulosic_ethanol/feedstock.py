"""Lignocellulosic feedstock characterization: cellulose, hemicellulose,
lignin and ash mass fractions for the agricultural residues India's
Pradhan Mantri JI-VAN Yojana 2G-ethanol program targets (rice straw,
supported by 12 integrated bio-ethanol projects funded Rs 1,969.50 crore
2018-19 to 2023-24) plus corn stover and sugarcane bagasse as
internationally documented comparators.

Composition figures (mass fractions, dry basis) and sourcing:

- **Rice straw**: cellulose ~35%, hemicellulose ~20%, lignin ~13%, ash
  ~15% -- midpoints of the ranges reported across several compositional
  studies (cellulose 24.0-36.7%, hemicellulose 21.3-27.8%, lignin
  12.5-13.5%, ash 10-18%). Rice straw's notably high ash content
  (mostly silica) is a real, distinguishing characteristic vs. other
  agricultural residues -- flagged here, not smoothed away.
- **Corn stover**: glucan (cellulose) ~36%, xylan (hemicellulose) ~21%,
  lignin ~17.8%, ash ~7% -- from NREL-standard-protocol compositional
  analyses of native/untreated corn stover.
- **Bagasse**: cellulose 39.52%, hemicellulose 25.63%, lignin 30.36%
  (an unusually high lignin content vs. the other two, a real
  documented bagasse characteristic, not a data-entry outlier).

These four fractions do not sum to 1.0 for any of the three presets --
the remainder is protein, extractives and other minor components this
conceptual-level model does not track separately, consistent with how
`biomass-to-syngas-opensource`'s sibling `biomass_feedstock.py` module
handles ultimate (elemental) analysis instead of this module's
proximate (structural-carbohydrate) analysis -- a genuinely different
characterization basis for a genuinely different downstream process
(gasification cares about elemental composition; enzymatic hydrolysis
cares about which structural carbohydrate polymer the carbon is in)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LignocellulosicFeedstock:
    name: str
    mass_flow_kg_s: float
    cellulose_mass_frac: float
    hemicellulose_mass_frac: float
    lignin_mass_frac: float
    ash_mass_frac: float

    def __post_init__(self) -> None:
        total = self.cellulose_mass_frac + self.hemicellulose_mass_frac + self.lignin_mass_frac + self.ash_mass_frac
        if not 0 < total <= 1.0:
            raise ValueError(f"cellulose+hemicellulose+lignin+ash mass fractions must be in (0, 1], got {total:.4f}")

    def cellulose_kg_s(self) -> float:
        return self.mass_flow_kg_s * self.cellulose_mass_frac

    def hemicellulose_kg_s(self) -> float:
        return self.mass_flow_kg_s * self.hemicellulose_mass_frac

    def lignin_kg_s(self) -> float:
        return self.mass_flow_kg_s * self.lignin_mass_frac

    def ash_kg_s(self) -> float:
        return self.mass_flow_kg_s * self.ash_mass_frac


def rice_straw(mass_flow_kg_s: float) -> LignocellulosicFeedstock:
    return LignocellulosicFeedstock("rice straw", mass_flow_kg_s,
                                    cellulose_mass_frac=0.35, hemicellulose_mass_frac=0.20,
                                    lignin_mass_frac=0.13, ash_mass_frac=0.15)


def corn_stover(mass_flow_kg_s: float) -> LignocellulosicFeedstock:
    return LignocellulosicFeedstock("corn stover", mass_flow_kg_s,
                                    cellulose_mass_frac=0.36, hemicellulose_mass_frac=0.21,
                                    lignin_mass_frac=0.178, ash_mass_frac=0.07)


def bagasse(mass_flow_kg_s: float) -> LignocellulosicFeedstock:
    return LignocellulosicFeedstock("sugarcane bagasse", mass_flow_kg_s,
                                    cellulose_mass_frac=0.3952, hemicellulose_mass_frac=0.2563,
                                    lignin_mass_frac=0.3036, ash_mass_frac=0.02)
