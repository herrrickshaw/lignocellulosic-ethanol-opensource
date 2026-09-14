# External validation

## Real-world motivation and public source

India's Pradhan Mantri JI-VAN Yojana funds 12 integrated 2G bio-ethanol
projects (Rs 1,969.50 crore, 2018-19 to 2023-24); separately, PSU oil
companies are building 12 more 2G bio-refineries (Rs 14,000 crore).
IOCL's Panipat, Haryana plant -- India's first commercial 2G ethanol
plant, based on Praj Industries' technology (the same real vendor
already cited in the sibling ethanol-design-opensource repo's own
`docs/VENDOR_REFERENCE.md` for 1G dehydration) -- commenced commercial
production 2023-11-11: 425.7 tonnes/day of rice straw feedstock, 100
KLPD nameplate ethanol capacity, reported cost Rs 984 crore.

## The elegant glucose/xylose theoretical-yield equivalence

`cofermentation.py`'s theoretical ethanol mass yield works out to the
SAME 0.5114 kg/kg for both glucose (C6) and xylose (C5) sugars -- this
module's own test suite confirms it to 9 significant figures rather
than assuming it. It is a real consequence of both being (CH2O)n
carbohydrates, not a coincidence: the Gay-Lussac-type stoichiometric
balance (n sugar -> ~n/3 x 5 ethanol + n/3 x 5 CO2, scaled to each
sugar's own carbon count) reduces to the same mass fraction regardless
of chain length. A clean, checkable, derived fact rather than a
recalled one.

## Lignin residue heating value -- a genuine, substrate-dependent finding

`enzymatic_hydrolysis.lignin_residue_energy()`'s mass-weighted HHV
blend (pure lignin 26.7 MJ/kg + residual carbohydrate ~17.5 MJ/kg) was
checked against a real published range for mixed distillery lignin
residue (16.3-19.8 MJ/kg, "7,000-8,500 BTU/lb dry basis") across all
three feedstock presets:

| Feedstock | Blended HHV | vs. cited 16.3-19.8 MJ/kg range |
|---|---|---|
| Corn stover | 18.6 MJ/kg | Inside |
| Bagasse | 22.5 MJ/kg | Above |
| Rice straw | 14.1 MJ/kg | Below |

**Reported as-is, not forced to agree**: only corn stover lands inside
the cited range. Bagasse's real, unusually high lignin content (30.36%,
the highest of the three presets) pulls its blend above it; rice
straw's real, distinctively high ash/silica content (15%, the highest
of the three) dilutes the combustible fraction and pulls its blend
below it. Both deviations trace directly to each feedstock's own cited
composition, not a modeling error -- and the cited real range itself
likely reflects measurements from a lower-ash (probably corn-based)
feedstock, which this project has no way to confirm from the public
source alone. An honest limitation of the cross-check, stated rather
than glossed over.

## Full-chain worked example: a real, disclosed overshoot -- and a separate real operating gap

`examples/full_chain_worked_example.py` runs rice straw at IOCL
Panipat's real published scale (425.7 t/day feedstock) and computes
264.1 L ethanol/tonne rice straw against Panipat's own published DESIGN
figure of 234.9 L/tonne (100 KLPD / 425.7 t/day) -- a 1.12x overshoot.

This is the SAME order-of-magnitude gap the sibling ethanol-design-
opensource repo found for its grain route (13-21% overshoot there vs.
12% here), and for the same underlying reason: this project's default
process-step efficiencies (75% xylose recovery, 75% cellulose
conversion, 90%/85% glucose/xylose fermentation) are each individually
defensible against published lab/pilot literature, but their COMBINED
effect (0.75 x 0.75 x ~0.87 average fermentation efficiency = ~0.49 of
the fully-theoretical chain) evidently still outperforms what a real,
newly commissioned commercial-scale plant achieves. Rather than lower
any one parameter to force an exact match -- which would just replace
one honestly-cited literature figure with an unverified fitted one --
this gap is reported and left visible, exactly the stance this
project's sibling repos take everywhere a "typical" published figure
stands in for a specific plant's own real, unmeasured performance.

**A separate, NOT directly comparable real finding**: press coverage
from December 2025 reports Panipat operating at only 62% of its DESIGN
THROUGHPUT capacity (tonnes of rice straw processed per day) during
November-December 2025, following "recent modifications... to address
process and mechanical challenges." This is a real, disclosed
commissioning-difficulty data point for India's first commercial 2G
plant -- worth reporting as honest context on how hard this technology
is to run at full scale, but it describes throughput utilization, not
the per-tonne yield efficiency this project's model computes, so the
two figures are not combined into one claim.

## What was deliberately not modeled in this first pass

- Rate-based/kinetic enzymatic hydrolysis (Michaelis-Menten-type
  cellulase kinetics, enzyme adsorption/inhibition effects) -- this
  project uses a direct conversion-efficiency input, the same
  simplification the sibling repos use for other real, condition-
  dependent process parameters (tar yield, biodegradability fraction).
- A combined pretreatment severity factor (time/temperature/acid
  concentration collapsed into one number) -- several published
  formulations exist and differ in exact form; `xylose_recovery_fraction`
  is exposed as a direct input instead, to avoid misquoting a formula
  from memory.
- Fermentation inhibitor effects (furfural, HMF, acetic acid -- real,
  well-documented byproducts of dilute-acid pretreatment that can
  depress real fermentation efficiency below what a clean-sugar
  laboratory test would show) -- folded implicitly into the overall
  efficiency gap discussed above, not modeled as a separate stream.
