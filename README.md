# Lignocellulosic (2G) Ethanol Design (open-source)

Interactive, open-source conceptual sizing tools for a second-generation
(2G) cellulosic fuel-ethanol biorefinery — agricultural-residue
feedstock characterization (rice straw, corn stover, bagasse), dilute-
acid pretreatment, enzymatic hydrolysis, C5+C6 co-fermentation,
Fenske-Underwood-Gilliland shortcut distillation, and 3A molecular-sieve
dehydration to anhydrous fuel ethanol. Sibling project to
[lng-design-opensource](https://github.com/herrrickshaw/lng-design-opensource),
[biomass-to-syngas-opensource](https://github.com/herrrickshaw/biomass-to-syngas-opensource),
[coal-to-urea-design-opensource](https://github.com/herrrickshaw/coal-to-urea-design-opensource),
[ethanol-design-opensource](https://github.com/herrrickshaw/ethanol-design-opensource)
(the 1G molasses/grain route) and
[cbg-design-opensource](https://github.com/herrrickshaw/cbg-design-opensource):
same discipline — public-domain/textbook correlations only, CoolProp for
real thermodynamic properties, every method cited, every module tested,
every worked example actually run end to end.

**Real-world motivation**: India's Pradhan Mantri JI-VAN Yojana funds 12
integrated 2G bio-ethanol projects (Rs 1,969.50 crore). This repo's
worked example runs at the real, publicly disclosed scale of IOCL's
Panipat, Haryana plant — India's first commercial 2G ethanol plant,
built on Praj Industries' technology, commissioned 2023-11-11 (425.7
t/day rice straw, 100 KLPD nameplate) — see `docs/VALIDATION.md` for an
honest overshoot the comparison surfaced, and a separate real operating
finding (62% of design throughput in Nov-Dec 2025).

**Scope**: fully generic and literature-only. Nothing here derives from
any proprietary vendor, licensor, or client engineering data.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q                                        # 37 tests
python examples/full_chain_worked_example.py     # rice straw -> ethanol, IOCL Panipat scale
streamlit run streamlit_app.py                   # interactive app
```

## Modules

| Module | Method | Key outputs |
|---|---|---|
| `lignocellulosic_ethanol/feedstock.py` | Cited structural-carbohydrate composition (rice straw, corn stover, bagasse) | Cellulose/hemicellulose/lignin/ash mass flows |
| `lignocellulosic_ethanol/pretreatment.py` | Dilute-acid hydrolysis of hemicellulose to xylose, exact MW ratio | Xylose flow, cellulose/lignin passthrough |
| `lignocellulosic_ethanol/enzymatic_hydrolysis.py` | Cellulase hydrolysis of cellulose to glucose (same MW ratio as starch) | Glucose flow, lignin-residue heating value |
| `lignocellulosic_ethanol/cofermentation.py` | C5+C6 co-fermentation, derived-identical glucose/xylose theoretical yield | Ethanol from each sugar stream |
| `lignocellulosic_ethanol/distillation.py` | Fenske-Underwood-Gilliland shortcut (same as ethanol-design-opensource) | Actual stages, reflux, distillate purity |
| `lignocellulosic_ethanol/dehydration.py` | 3A zeolite VPSA (same as ethanol-design-opensource) | Bed sizing, BIS IS 15464 compliance |

## Validated against a real, operating India 2G plant

`examples/full_chain_worked_example.py` runs rice straw at IOCL
Panipat's real 425.7 t/day scale and computes 264.1 L/tonne against
Panipat's own published 234.9 L/tonne design figure — a 1.12x overshoot,
the same order of magnitude as the 13-21% gap the sibling ethanol-
design-opensource repo found for its grain route, reported honestly
rather than tuned away. Separately, `cofermentation.py`'s own test suite
confirms a genuinely elegant DERIVED fact: the theoretical ethanol mass
yield per kg of sugar is identical for glucose and xylose (0.5114 kg/kg
both), since both are (CH2O)n carbohydrates regardless of chain length.

## Vendor reference

`docs/VENDOR_REFERENCE.md` notes Praj Industries as the real technology
provider behind IOCL Panipat — the same company already verified in the
sibling ethanol-design-opensource repo's own vendor document for 1G
dehydration, now confirmed spanning both generations of this project
family's fuel-ethanol coverage.

## Related open-source work

[DWSIM](https://github.com/DanWBR/dwsim5), [IDAES](https://github.com/IDAES/idaes-pse) —
general open-source process simulators, same as every sibling repo cites.
[BioSTEAM](https://github.com/BioSTEAMDevelopmentGroup/biosteam) /
[Bioindustrial-Park](https://github.com/BioSTEAMDevelopmentGroup/Bioindustrial-Park)
(Guest Group, UIUC) include real, published `cellulosic`/`cornstover`
biorefinery flowsheets — the closest existing open-source prior art
(consulted for context, not a dependency; every correlation here is
independently sourced and cited in `docs/METHODOLOGY.md`).

## Disclaimer

This tool implements textbook/public-domain conceptual sizing methods
for early-stage screening only. It is not a substitute for a rigorous
process simulator, enzyme/fermentation kinetics model, or vendor-
certified equipment data for detailed design. Always validate against a
licensed simulator and vendor data before committing to equipment
specifications.

## License

MIT — see [LICENSE](LICENSE).
