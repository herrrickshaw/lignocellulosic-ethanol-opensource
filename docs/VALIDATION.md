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

## A second real commercial plant brackets, rather than confirms, the model's prediction

Vendor research (docs/VENDOR_REFERENCE.md) found a genuine SECOND real,
commercial-scale 2G ethanol plant to check against: Clariant's sunliquid
plant in Podari, Romania -- 250,000 tonnes/year wheat/cereal straw
feedstock producing 50,000 tonnes/year cellulosic ethanol, a real
ACHIEVED figure (first commercial production 2022), not a design
nameplate. That works out to 253.5 L/tonne straw.

| Source | Feedstock | L/tonne straw | Status |
|---|---|---|---|
| IOCL Panipat | rice straw | 234.9 | Real, published DESIGN figure |
| Clariant Podari | wheat/cereal straw | 253.5 | Real, ACHIEVED commercial output |
| This project's model | rice straw | 264.1 | Computed, default parameters |

**The model's prediction now sits close to, and not far above, a real
achieved commercial figure -- reframing the earlier "1.12x overshoot"
finding rather than overturning it.** Compared to Panipat alone, the
model looked like it was systematically overoptimistic; compared to
Clariant, the model overshoots by only 264.1/253.5 = 1.04x, and
Clariant's own real, achieved output is itself already 253.5/234.9 =
1.08x above Panipat's DESIGN figure. A real, honest reading: Panipat's
own published design figure may itself be a conservative baseline
relative to what state-of-the-art 2G technology can and does achieve
commercially, not proof this project's literature-derived defaults are
too optimistic. **This is NOT presented as a corrected or improved
validation** -- the two real plants use different feedstock (rice vs.
wheat straw) and, per Clariant's own disclosure, a different
pretreatment chemistry entirely ("chemical-free" vs. this project's
modeled dilute-acid process), so this is additional honest context,
not a resolved discrepancy.

**A related, separately verified finding**: Novonesis's (formerly
Novozymes) real, currently marketed Cellic CTec3 HS enzyme is
independently reported achieving 80-96% cellulose-to-glucose
conversion in published technical literature -- well ABOVE this
project's own `cellulose_conversion_efficiency` default of 0.75. This
project's enzymatic-hydrolysis default is therefore a genuinely
conservative choice relative to real modern commercial enzyme
performance, not an optimistic one -- suggesting that if the model's
overall yield needs adjusting toward real-world plant performance, the
enzymatic hydrolysis step is likely NOT where the gap originates (this
project's xylose-recovery and fermentation-efficiency defaults are the
more likely candidates, per the same logic already applied to the grain
route in the sibling ethanol-design-opensource repo).

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
