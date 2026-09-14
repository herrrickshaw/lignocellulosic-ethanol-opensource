# Methodology & citations

## Feedstock (`lignocellulosic_ethanol/feedstock.py`)

Rice straw (cellulose ~35%, hemicellulose ~20%, lignin ~13%, ash ~15%)
is the midpoint of several compositional studies (cellulose 24.0-36.7%,
hemicellulose 21.3-27.8%, lignin 12.5-13.5%, ash 10-18%); corn stover
(glucan 36%, xylan 21%, lignin 17.8%, ash ~7%) is from NREL-standard-
protocol compositional analyses of native/untreated stover; bagasse
(cellulose 39.52%, hemicellulose 25.63%, lignin 30.36%) is from a
published wheat-straw/bagasse cellulose-extraction characterization
study. See each preset's docstring in `feedstock.py` for the full detail.

## Pretreatment (`pretreatment.py`)

Dilute-acid pretreatment hydrolyses hemicellulose to xylose via the
exact molecular-weight ratio MW(xylose)/MW(xylan monomer) = 150.13/132.12
= 1.1363, derived directly rather than quoted. Real xylose recovery
(55-85% across several published studies at various severities) is
taken as a direct, overridable input (default 0.75) rather than derived
from a combined-severity-factor formula this project could not
independently verify from memory without real transcription risk.

## Enzymatic hydrolysis (`enzymatic_hydrolysis.py`)

Cellulose hydrolyses to glucose via the SAME exact molecular-weight
ratio as starch hydrolysis (180.156/162.14 = 1.1112, sibling ethanol-
design-opensource repo's `starch_hydrolysis.py`) -- both are glucose
polymers. Real cellulase conversion efficiency (26-94% across published
studies depending on enzyme loading and time) is a direct, overridable
input (default 0.75). Lignin residue heating value is a mass-weighted
blend of pure lignin's HHV (26.7 MJ/kg, "competitive with coal" -- real,
cited) and an estimated residual-carbohydrate HHV (17.5 MJ/kg),
cross-checked per-feedstock against a real published range for mixed
distillery lignin/carbohydrate residue (16.3-19.8 MJ/kg) -- see
docs/VALIDATION.md for the honest, substrate-dependent finding this
check produced (only corn stover lands inside that range; rice straw's
high ash pulls it below, bagasse's high lignin pushes it above).

## Co-fermentation (`cofermentation.py`)

A real, DERIVED (not asserted) fact: the theoretical ethanol mass yield
per kg of sugar is identical for glucose and xylose (0.5114 kg/kg both),
since both are (CH2O)n carbohydrates regardless of chain length. Real
xylose fermentation efficiency in engineered S. cerevisiae strains is
reported at 88-94% of theoretical in the best published studies (a
xylose-isomerase-pathway strain at ~90%, a pilot-scale strain near
94%); this module defaults to 0.85, deliberately below the best
published figures, consistent with the same lab-vs-full-scale gap
`docs/VALIDATION.md` documents for the overall chain.

## Distillation & dehydration

Identical modules to the sibling ethanol-design-opensource repo's own
`distillation.py` (Fenske-Underwood-Gilliland shortcut, CoolProp-derived
relative volatility) and `dehydration.py` (3A zeolite VPSA, GPSA Ch. 20
two-bed structure) -- reproduced rather than imported across repos (see
each module's own docstring), since ethanol-water separation physics
doesn't depend on feedstock origin.

## Related open-source work

[DWSIM](https://github.com/DanWBR/dwsim5), [IDAES](https://github.com/IDAES/idaes-pse) --
general open-source process simulators, same as every sibling repo
cites. [BioSTEAM](https://github.com/BioSTEAMDevelopmentGroup/biosteam)
and its [Bioindustrial-Park](https://github.com/BioSTEAMDevelopmentGroup/Bioindustrial-Park)
model library (Guest Group, UIUC) include real, published `cellulosic`
and `cornstover` biorefinery flowsheets -- directly relevant prior art
for 2G cellulosic ethanol specifically, already cited by the sibling
ethanol-design-opensource repo for its own 1G routes.
