# Lignocellulosic (2G) Ethanol Design (open-source)

Conceptual sizing tools for a second-generation (2G) cellulosic fuel-ethanol biorefinery, for process
engineers and students doing early-stage screening. It takes an agricultural-residue feedstock (rice straw,
corn stover, bagasse) through dilute-acid pretreatment, enzymatic hydrolysis, C5+C6 co-fermentation,
Fenske-Underwood-Gilliland shortcut distillation and 3A molecular-sieve dehydration, and produces ethanol
yield, column stages and reflux, sieve-bed sizing and lignin-residue heating value, via a Python package,
a worked example and a Streamlit app.

> Status: maintained. Public-domain/textbook correlations only, nothing derived from proprietary vendor,
> licensor or client data; conceptual screening only, not a substitute for a licensed process simulator.

New to the repo? See [How to use this repo with AI](HOW_TO_USE_WITH_AI.md).

## What it does
- Characterises feedstock composition (cellulose, hemicellulose, lignin, ash) from cited values.
- Converts hemicellulose to xylose (exact MW ratio) and cellulose to glucose (same ratio as starch).
- Co-ferments glucose and xylose; theoretical ethanol yield is identical for both sugars (0.5114 kg/kg), derived and tested.
- Designs an ethanol-water column by Fenske-Underwood-Gilliland, with VLE from CoolProp's HEOS mixture model.
- Sizes a 3A zeolite VPSA dehydration bed and checks the BIS IS 15464 water limit.
- Runs end to end at the publicly disclosed scale of IOCL's Panipat 2G plant (425.7 t/day rice straw, 100 KLPD nameplate).

## Quick start
```bash
git clone https://github.com/herrrickshaw/lignocellulosic-ethanol-opensource.git
cd lignocellulosic-ethanol-opensource
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python examples/full_chain_worked_example.py     # rice straw -> ethanol, IOCL Panipat scale
streamlit run streamlit_app.py                   # interactive app
```

## How it works
| Stage | Module | Output |
|---|---|---|
| Feedstock | `feedstock.py` | Cellulose/hemicellulose/lignin/ash mass flows (rice straw, corn stover, bagasse) |
| Pretreatment | `pretreatment.py` | Xylose flow, cellulose/lignin passthrough |
| Enzymatic hydrolysis | `enzymatic_hydrolysis.py` | Glucose flow, lignin-residue heating value |
| Co-fermentation | `cofermentation.py` | Ethanol from each sugar stream |
| Distillation | `distillation.py` (+ `properties.py` VLE) | Actual stages, reflux, distillate purity |
| Dehydration | `dehydration.py` | Bed sizing, BIS IS 15464 compliance |

Calculation functions are pure (data in, result dataclass out); defaults are named module constants.
Real thermodynamics come from CoolProp; every method is cited in `docs/METHODOLOGY.md`.

## Repository layout
| Path | Purpose |
|---|---|
| `lignocellulosic_ethanol/` | The package, one module per process stage plus `properties.py` |
| `examples/full_chain_worked_example.py` | End-to-end IOCL Panipat-scale run |
| `streamlit_app.py` | Interactive app |
| `docs/` | `METHODOLOGY.md`, `VALIDATION.md`, `VENDOR_REFERENCE.md` |
| `tests/` | Unit tests per module plus characterisation tests (`tests/data/`) |

## Validation against two real 2G plants
The worked example computes 264.1 L/tonne rice straw against Panipat's own published 234.9 L/tonne DESIGN
figure (1.12x). Clariant's sunliquid plant in Podari, Romania ACHIEVED 253.5 L/tonne wheat straw in real
operation, bracketing the model more closely (1.04x). Reported as context, not a resolved discrepancy: the
plants use different feedstock and pretreatment chemistry. Separately, Panipat was reported running at 62%
of design throughput in Nov-Dec 2025. See `docs/VALIDATION.md`. `docs/VENDOR_REFERENCE.md` covers Praj
Industries, Clariant sunliquid and Novonesis (Cellic CTec3 HS reportedly reaches 80-96% cellulose
conversion, versus this repo's deliberately conservative 75% default).

Motivation: India's PM JI-VAN Yojana funds 12 integrated 2G bio-ethanol projects (Rs 1,969.50 crore).

## Configuration
No environment variables or secrets. Tunable defaults are keyword arguments backed by module constants,
e.g. `DEFAULT_XYLOSE_RECOVERY_FRACTION = 0.75`, `DEFAULT_CELLULOSE_CONVERSION_EFFICIENCY = 0.75`,
`DEFAULT_GLUCOSE_FERMENTATION_EFFICIENCY = 0.90`, `DEFAULT_XYLOSE_FERMENTATION_EFFICIENCY = 0.85`,
`DEFAULT_REFLUX_RATIO_FACTOR = 1.3`.

## Testing
```bash
pytest -q          # 46 tests
ruff check .
```
`tests/test_characterisation.py` pins numeric outputs and the worked-example stdout to values produced by
the pre-refactor code.

## Limitations and known issues
- Conceptual sizing only: no enzyme or fermentation kinetics, no breakthrough-curve simulation. Validate against
  a licensed simulator and vendor data before specifying equipment.
- The model overshoots Panipat's design yield by 12%; see `docs/VALIDATION.md`.
- Fermentation broth ethanol (3 wt% in the example) is an illustrative value, not derived from the chain.

## Related repositories
Siblings with the same discipline: [lng-design-opensource](https://github.com/herrrickshaw/lng-design-opensource),
[biomass-to-syngas-opensource](https://github.com/herrrickshaw/biomass-to-syngas-opensource),
[coal-to-urea-design-opensource](https://github.com/herrrickshaw/coal-to-urea-design-opensource),
[ethanol-design-opensource](https://github.com/herrrickshaw/ethanol-design-opensource) (1G molasses/grain) and
[cbg-design-opensource](https://github.com/herrrickshaw/cbg-design-opensource). Open-source prior art consulted
for context, not dependencies: [DWSIM](https://github.com/DanWBR/dwsim5), [IDAES](https://github.com/IDAES/idaes-pse),
[BioSTEAM](https://github.com/BioSTEAMDevelopmentGroup/biosteam) and
[Bioindustrial-Park](https://github.com/BioSTEAMDevelopmentGroup/Bioindustrial-Park).

## Licence
MIT, see [LICENSE](LICENSE).
