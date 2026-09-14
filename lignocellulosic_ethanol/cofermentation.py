"""C5+C6 co-fermentation: an engineered organism (typically Saccharomyces
cerevisiae with an inserted xylose-utilization pathway, xylose reductase/
xylitol dehydrogenase or xylose isomerase) ferments BOTH the glucose
(from `enzymatic_hydrolysis.py`) AND the xylose (from `pretreatment.py`)
to ethanol -- the defining extra complication 2G ethanol has over 1G
(molasses/grain) fermentation, which only ever sees glucose.

A real, elegant, DERIVED fact this module's own test suite confirms
rather than assumes: the theoretical Gay-Lussac-type mass yield of
ethanol per kg of sugar is IDENTICAL for glucose and xylose --
0.5114 kg ethanol / kg sugar for both. This is not a coincidence: both
are (CH2O)n carbohydrates with the same empirical formula regardless of
chain length, so

    glucose:  C6H12O6      -> 2 C2H5OH + 2 CO2   (2x46.068/180.156 = 0.5114)
    xylose:   3 C5H10O5    -> 5 C2H5OH + 5 CO2    ((5/3)x46.068/150.13 = 0.5114)

both reduce to the same mass-yield fraction once carried through the
real molecular weights -- a genuine cross-check this module's tests
verify to several significant figures.

Real fermentation efficiency, however, is NOT the same for both sugars.
Glucose fermentation by S. cerevisiae is its native, highly optimized
pathway; xylose fermentation is a heterologous, engineered pathway that
several independent studies report running at 88-94% of theoretical in
the best published engineered strains (highest reported: ~0.46 g
ethanol/g xylose = 90% of theoretical; a pilot-scale strain reported
near 94%). This module defaults `xylose_fermentation_efficiency` to
0.85 -- deliberately below the best published lab/pilot figures, the
same "real full-scale plants run below lab-optimized ceilings" pattern
this project's sibling ethanol-design-opensource repo found for grain
starch hydrolysis -- and `glucose_fermentation_efficiency` to 0.90 (a
conventional, slightly-below-molasses-calibrated default for a
newly-engineered co-fermenting strain, distinct from the pure-glucose-
adapted strain the molasses-based sibling repo's own 92.57% figure was
calibrated to)."""
from __future__ import annotations

from dataclasses import dataclass

from .enzymatic_hydrolysis import HydrolysisResult
from .pretreatment import PretreatmentResult

MW_GLUCOSE = 180.156
MW_XYLOSE = 150.13
MW_ETHANOL = 46.068
ETHANOL_DENSITY_KG_L = 0.789

THEORETICAL_ETHANOL_YIELD_FROM_GLUCOSE_KG_PER_KG = 2 * MW_ETHANOL / MW_GLUCOSE
THEORETICAL_ETHANOL_YIELD_FROM_XYLOSE_KG_PER_KG = (5.0 / 3.0) * MW_ETHANOL / MW_XYLOSE

DEFAULT_GLUCOSE_FERMENTATION_EFFICIENCY = 0.90
DEFAULT_XYLOSE_FERMENTATION_EFFICIENCY = 0.85


@dataclass
class CofermentationResult:
    ethanol_from_glucose_kg_s: float
    ethanol_from_xylose_kg_s: float
    total_ethanol_kg_s: float
    total_ethanol_l_s: float
    glucose_fermentation_efficiency: float
    xylose_fermentation_efficiency: float


def coferment(hydrolysis: HydrolysisResult, pretreated: PretreatmentResult,
             glucose_fermentation_efficiency: float = DEFAULT_GLUCOSE_FERMENTATION_EFFICIENCY,
             xylose_fermentation_efficiency: float = DEFAULT_XYLOSE_FERMENTATION_EFFICIENCY) -> CofermentationResult:
    if not 0 < glucose_fermentation_efficiency <= 1.0:
        raise ValueError("glucose_fermentation_efficiency must be in (0, 1]")
    if not 0 < xylose_fermentation_efficiency <= 1.0:
        raise ValueError("xylose_fermentation_efficiency must be in (0, 1]")

    ethanol_glu = (hydrolysis.glucose_produced_kg_s * THEORETICAL_ETHANOL_YIELD_FROM_GLUCOSE_KG_PER_KG
                  * glucose_fermentation_efficiency)
    ethanol_xyl = (pretreated.xylose_produced_kg_s * THEORETICAL_ETHANOL_YIELD_FROM_XYLOSE_KG_PER_KG
                  * xylose_fermentation_efficiency)
    total_kg_s = ethanol_glu + ethanol_xyl

    return CofermentationResult(
        ethanol_from_glucose_kg_s=ethanol_glu,
        ethanol_from_xylose_kg_s=ethanol_xyl,
        total_ethanol_kg_s=total_kg_s,
        total_ethanol_l_s=total_kg_s / ETHANOL_DENSITY_KG_L,
        glucose_fermentation_efficiency=glucose_fermentation_efficiency,
        xylose_fermentation_efficiency=xylose_fermentation_efficiency,
    )
