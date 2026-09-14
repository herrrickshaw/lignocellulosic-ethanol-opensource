"""End-to-end worked example: rice straw -> pretreatment -> enzymatic
hydrolysis -> C5+C6 co-fermentation -> distillation -> dehydration,
sized at IOCL's real, publicly disclosed 2G ethanol biorefinery in
Panipat, Haryana -- India's first commercial 2G ethanol plant, based on
Praj Industries' technology (the same real vendor this project's
sibling ethanol-design-opensource repo cites in its own
docs/VENDOR_REFERENCE.md for 1G dehydration), commissioned 2023-11-11:
425.7 tonnes/day of rice straw feedstock, 100 KLPD (kilolitres per day)
nameplate ethanol capacity -- see docs/VALIDATION.md for the full
sourcing, including the plant's own recently reported operational
challenges.

Run: python examples/full_chain_worked_example.py
"""
from __future__ import annotations

from lignocellulosic_ethanol import cofermentation as CF
from lignocellulosic_ethanol import dehydration as DH
from lignocellulosic_ethanol import distillation as D
from lignocellulosic_ethanol import enzymatic_hydrolysis as EH
from lignocellulosic_ethanol import feedstock as F
from lignocellulosic_ethanol import pretreatment as PT

PANIPAT_FEEDSTOCK_TPD = 425.7
PANIPAT_FEEDSTOCK_KG_S = PANIPAT_FEEDSTOCK_TPD * 1000.0 / 86400.0
PANIPAT_NAMEPLATE_ETHANOL_KLPD = 100.0
PANIPAT_DESIGN_L_PER_TONNE = PANIPAT_NAMEPLATE_ETHANOL_KLPD * 1000.0 / PANIPAT_FEEDSTOCK_TPD

# Clariant sunliquid, Podari, Romania -- a real, ACHIEVED (not design) commercial
# cellulosic-ethanol output figure, different feedstock (wheat/cereal straw) and a
# different ("chemical-free") pretreatment chemistry -- see docs/VALIDATION.md.
CLARIANT_PODARI_STRAW_TONNES_PER_YEAR = 250_000.0
CLARIANT_PODARI_ETHANOL_TONNES_PER_YEAR = 50_000.0
CLARIANT_PODARI_L_PER_TONNE = (CLARIANT_PODARI_ETHANOL_TONNES_PER_YEAR * 1000.0 / 0.789) / CLARIANT_PODARI_STRAW_TONNES_PER_YEAR


def main() -> None:
    print("=" * 78)
    print("2G LIGNOCELLULOSIC ETHANOL WORKED EXAMPLE (IOCL Panipat scale)")
    print("=" * 78)
    print(f"Feed: rice straw, {PANIPAT_FEEDSTOCK_TPD:.1f} t/day ({PANIPAT_FEEDSTOCK_KG_S:.3f} kg/s)")
    print(f"IOCL Panipat's own published design figure: {PANIPAT_DESIGN_L_PER_TONNE:.1f} L ethanol/tonne rice straw")

    feed = F.rice_straw(PANIPAT_FEEDSTOCK_KG_S)
    pretreated = PT.pretreat(feed)
    hydrolyzed = EH.hydrolyze_cellulose(pretreated)
    coferm = CF.coferment(hydrolyzed, pretreated)

    l_per_tonne = coferm.total_ethanol_l_s / (PANIPAT_FEEDSTOCK_KG_S / 1000.0)
    print(f"\nPretreatment: {pretreated.xylose_produced_kg_s * 86400 / 1000:,.1f} t/day xylose "
          f"({pretreated.xylose_recovery_fraction:.0%} recovery)")
    print(f"Enzymatic hydrolysis: {hydrolyzed.glucose_produced_kg_s * 86400 / 1000:,.1f} t/day glucose "
          f"({hydrolyzed.cellulose_conversion_efficiency:.0%} conversion)")
    print(f"Co-fermentation: {coferm.total_ethanol_l_s * 86400:,.0f} L/day ethanol "
          f"({l_per_tonne:.1f} L/tonne rice straw; from glucose "
          f"{coferm.ethanol_from_glucose_kg_s / coferm.total_ethanol_kg_s:.0%}, "
          f"from xylose {coferm.ethanol_from_xylose_kg_s / coferm.total_ethanol_kg_s:.0%})")

    # Cellulosic hydrolysate/beer streams are real-world notoriously dilute compared to
    # molasses/grain wash (lower achievable solids loading at the pretreatment/hydrolysis
    # stage) -- 3-5 wt% ethanol is a commonly cited illustrative range for 2G fermentation
    # broths; this example uses 3% as a representative point, not a value derived elsewhere
    # in this chain.
    column = D.design_column(x_feed_mass_frac=0.03, x_distillate_mass_frac=0.94, x_bottoms_mass_frac=0.0005)
    ethanol_vapor_kg_s = coferm.total_ethanol_kg_s / column.distillate_mass_frac_ethanol
    bed = DH.size_dehydration_bed(ethanol_vapor_kg_s, 1 - column.distillate_mass_frac_ethanol)
    print(f"\nDistillation: {column.n_actual_stages:.0f} stages, distillate {column.distillate_mass_frac_ethanol:.1%} w/w")
    print(f"Dehydration: {bed.bed_mass_kg:,.0f} kg sieve, {bed.n_beds} beds, meets BIS spec: {bed.meets_bis_spec}")

    lignin_residue = EH.lignin_residue_energy(pretreated, hydrolyzed, feed)
    print(f"\nLignin/residue for process heat: {lignin_residue.residue_mass_flow_kg_s * 86400 / 1000:,.1f} t/day "
          f"at {lignin_residue.blended_hhv_MJ_kg:.1f} MJ/kg")

    ratio = l_per_tonne / PANIPAT_DESIGN_L_PER_TONNE
    print(f"\n=== Validation: {l_per_tonne:.1f} L/tonne (this model) vs. {PANIPAT_DESIGN_L_PER_TONNE:.1f} "
          f"L/tonne (Panipat's own published design figure) = {ratio:.2f}x ===")
    print("This model overshoots the real plant's DESIGN figure by a margin consistent with the "
          "same lab-vs-real-scale gap found in the sibling ethanol-design-opensource repo's grain "
          "route (13-21% there; see docs/VALIDATION.md here for the full discussion). Separately, "
          "and NOT directly comparable to this per-tonne yield figure: Panipat itself was reported "
          "running at only 62% of its DESIGN THROUGHPUT capacity in Nov-Dec 2025, a real, disclosed "
          "commissioning challenge for India's first commercial 2G plant, not a claim this model "
          "predicts or explains.")

    clariant_ratio = l_per_tonne / CLARIANT_PODARI_L_PER_TONNE
    print(f"\n=== A second real plant: Clariant's sunliquid facility (Podari, Romania) achieved "
          f"{CLARIANT_PODARI_L_PER_TONNE:.1f} L/tonne wheat/cereal straw in real commercial "
          f"operation ({CLARIANT_PODARI_ETHANOL_TONNES_PER_YEAR:,.0f} t/year ethanol from "
          f"{CLARIANT_PODARI_STRAW_TONNES_PER_YEAR:,.0f} t/year straw) -- this model's "
          f"{l_per_tonne:.1f} L/tonne is only {clariant_ratio:.2f}x that REAL ACHIEVED figure, "
          f"vs. {ratio:.2f}x Panipat's DESIGN figure. Different feedstock (wheat vs. rice straw) "
          f"and a different, 'chemical-free' pretreatment chemistry at Podari mean this is "
          f"additional honest context, not a resolved discrepancy -- see docs/VALIDATION.md. ===")


if __name__ == "__main__":
    main()
