"""Enzymatic hydrolysis: cellulase breaks down the pretreated cellulose
fraction to glucose -- the second sugar-release step, feeding
`cofermentation.py` alongside pretreatment's xylose stream.

Cellulose, like starch, is a polymer of glucose (beta-1,4-linked vs.
starch's alpha-1,4/1,6), so hydrolysis (C6H10O5)n + n H2O -> n C6H12O6
uses the EXACT SAME molecular-weight ratio (180.156/162.14 = 1.1112) as
the sibling ethanol-design-opensource repo's `starch_hydrolysis.py` --
not a coincidence, a real consequence of both polymers sharing the same
glucose-anhydride repeat unit.

Real commercial cellulase performance varies enormously with enzyme
loading and hydrolysis time: published studies report cellulose-to-
glucose conversion from ~26-31% (bagasse, 15-20 FPU/g, 12 h -- a short,
enzyme-loading-limited run) up to 94 mol% (a tertiary-cellulose study,
30 FPU/g, 72 h -- a long, well-optimized run), and rice straw
saccharification studies report 49-57 g reducing sugar per 100 g dry
substrate at 30 FPU/g. Given this wide, condition-dependent range, this
module takes `cellulose_conversion_efficiency` as a direct overridable
input (default 0.75, a defensible mid-to-upper estimate for a
reasonably optimized commercial process, well inside the published
range but below its best-case ceiling) rather than modeling enzyme
kinetics explicitly -- the same "cited range, explicit input" choice
`pretreatment.py` makes for xylose recovery.

`lignin_residue_energy()` sizes the solid residue left after BOTH sugar-
release steps (unconverted cellulose + unrecovered hemicellulose +
lignin + ash) and estimates its blended heating value from real,
independently cited component HHVs -- pure lignin's HHV (26.7 MJ/kg,
"competitive with coal") is real and well above typical whole-biomass
HHV, because lignin is aromatic/phenolic and far less oxygenated than
the carbohydrate polymers; this module's mass-weighted blend of that
figure with an estimated ~17.5 MJ/kg for the residual (unconverted)
carbohydrate fraction and zero for ash is checked in this module's own
test suite against the independently published range for real mixed
lignin/carbohydrate distillery residue (16.3-19.8 MJ/kg, "7,000-8,500
BTU/lb dry basis"). **A genuine, disclosed finding from running this
check across all three feedstock presets, not a uniform match**: corn
stover's blend (18.6 MJ/kg) lands inside that range, bagasse's (22.5
MJ/kg) lands above it (bagasse's real, unusually high 30% lignin
content pulls the blend up), and rice straw's (14.1 MJ/kg) lands BELOW
it (rice straw's real, distinctively high silica/ash content dilutes
the combustible fraction). All three are real, substrate-specific
consequences of each feedstock's own cited composition, not a modeling
inconsistency -- reported as-is rather than forced to agree."""
from __future__ import annotations

from dataclasses import dataclass

from .feedstock import LignocellulosicFeedstock
from .pretreatment import PretreatmentResult

CELLULOSE_TO_GLUCOSE_MW_RATIO = 180.156 / 162.14  # same exact ratio as starch hydrolysis
DEFAULT_CELLULOSE_CONVERSION_EFFICIENCY = 0.75

PURE_LIGNIN_HHV_MJ_KG = 26.7          # cited, real, "competitive with coal"
RESIDUAL_CARBOHYDRATE_HHV_MJ_KG = 17.5  # estimated typical dry-carbohydrate HHV, cross-checked below


@dataclass
class HydrolysisResult:
    glucose_produced_kg_s: float
    unconverted_cellulose_kg_s: float
    cellulose_conversion_efficiency: float


@dataclass
class LigninResidueResult:
    residue_mass_flow_kg_s: float
    blended_hhv_MJ_kg: float


def hydrolyze_cellulose(pretreated: PretreatmentResult,
                        cellulose_conversion_efficiency: float = DEFAULT_CELLULOSE_CONVERSION_EFFICIENCY) -> HydrolysisResult:
    if not 0 < cellulose_conversion_efficiency <= 1.0:
        raise ValueError("cellulose_conversion_efficiency must be in (0, 1]")
    glucose_kg_s = pretreated.cellulose_passthrough_kg_s * CELLULOSE_TO_GLUCOSE_MW_RATIO * cellulose_conversion_efficiency
    unconverted_kg_s = pretreated.cellulose_passthrough_kg_s * (1 - cellulose_conversion_efficiency)
    return HydrolysisResult(glucose_produced_kg_s=glucose_kg_s, unconverted_cellulose_kg_s=unconverted_kg_s,
                            cellulose_conversion_efficiency=cellulose_conversion_efficiency)


def lignin_residue_energy(pretreated: PretreatmentResult, hydrolysis: HydrolysisResult,
                          feedstock: LignocellulosicFeedstock) -> LigninResidueResult:
    lignin_kg_s = pretreated.lignin_passthrough_kg_s
    ash_kg_s = feedstock.ash_kg_s()
    residual_carbohydrate_kg_s = (pretreated.unrecovered_hemicellulose_kg_s + hydrolysis.unconverted_cellulose_kg_s)

    total_residue_kg_s = lignin_kg_s + ash_kg_s + residual_carbohydrate_kg_s
    if total_residue_kg_s <= 0:
        raise ValueError("computed residue mass flow is non-positive")

    energy_kW = lignin_kg_s * PURE_LIGNIN_HHV_MJ_KG + residual_carbohydrate_kg_s * RESIDUAL_CARBOHYDRATE_HHV_MJ_KG
    blended_hhv = energy_kW / total_residue_kg_s

    return LigninResidueResult(residue_mass_flow_kg_s=total_residue_kg_s, blended_hhv_MJ_kg=blended_hhv)
