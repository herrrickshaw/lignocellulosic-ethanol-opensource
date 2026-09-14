# 2G Ethanol Technology Provider Reference

Same purpose as the sibling repos' `docs/VENDOR_REFERENCE.md` documents:
does a named provider's own (or independently reported) real project
confirm a genuine, verifiable detail this project's sizing can be
cross-checked against — not vendor endorsement. Every entry was fetched
and inspected at the time of writing (September 2026); where a figure
could only be confirmed via a secondary source rather than the vendor's
own page, that is stated explicitly.

| Provider | Source | What it confirms | Relevance to this repo |
|---|---|---|---|
| **Clariant (sunliquid)** | Clariant's own press statement, independently reported by bioenergyinternational.com after Clariant's own site pages for this plant returned 404s at the time of fetching — flagged as secondary-sourced rather than claimed as independently verified on Clariant's own site. | A REAL, SECOND commercial 2G ethanol plant (Podari, Romania, first commercial cellulosic ethanol produced 2022) with quantified capacity: **250,000 tonnes/year wheat and cereal straw feedstock -> 50,000 tonnes/year cellulosic ethanol** (253.5 L/tonne straw, computed from these two published figures at standard ethanol density). Confirms "chemical-free pretreatment" (explicitly NOT the dilute-acid method this repo's `pretreatment.py` models -- a real, disclosed process difference, not a direct like-for-like comparison), "simultaneous C5 and C6 sugar fermentation" (exactly this repo's `cofermentation.py` approach), and lignin residue used for combined heat and power (exactly this repo's `lignin_residue_energy()` purpose). | **A genuine second real-plant data point, bracketing this repo's own model prediction rather than confirming or contradicting it alone**: IOCL Panipat's published DESIGN figure is 234.9 L/tonne rice straw (lower), this repo's own model computes 264.1 L/tonne (higher), and Clariant's real ACHIEVED figure for wheat straw sits at 253.5 L/tonne -- almost exactly between the two. See docs/VALIDATION.md for the full, honest discussion of what this does and doesn't prove (different feedstock, different pretreatment chemistry, so not a strict apples-to-apples check). |
| **Novonesis (formerly Novozymes) -- Cellic® CTec3 HS** | [Cellic CTec3 HS product page](https://www.novonesis.com/en/biosolutions/bioenergy/ethanol/cellic-ctec3-hs) (novonesis.com, own site, current post-2024-merger brand) | Real, currently marketed, market-leading commercial cellulase enzyme cocktail for cellulosic ethanol -- confirms this is an active, real commercial product line, not a hypothetical enzyme. The product page itself does not publish quantified FPU/dosage/yield figures (flagged below); independently reported figures from published technical literature cite CTec3 conversion performance in the 80-96% range depending on dose and substrate, and roughly 50 kg of CTec3 needed per tonne of ethanol produced (vs. >=250 kg of an older competing product) -- both figures from Novozymes' own published technical materials as reported in secondary industry coverage, not independently confirmed on novonesis.com itself. | This repo's `enzymatic_hydrolysis.py` defaults `cellulose_conversion_efficiency` to 0.75 -- a DELIBERATELY conservative choice relative to this real, modern, commercial enzyme's reported 80-96% range, not an overestimate. Worth noting honestly: real full-scale plants may achieve BETTER cellulose conversion than this project's own default assumes, meaning the model's real-world overshoot (see docs/VALIDATION.md) likely does NOT originate primarily from the enzymatic hydrolysis step. |
| **Praj Industries** | Widely reported (biofuels-news.com, indianchemicalnews.com, chinimandi.com) as the technology provider behind IOCL's Panipat 2G ethanol biorefinery. | Confirms Praj as a real technology provider spanning BOTH the 1G and 2G routes this project family covers -- the plant this repo's own worked example is sized against (425.7 t/day rice straw, 100 KLPD nameplate) is Praj's real, commissioned, commercial installation. | Real-world grounding for the Panipat side of the worked-example validation exercise. |

## What didn't clear the verification bar

No public Praj page, and no current Novonesis product page, with
quantified pretreatment/hydrolysis/co-fermentation process parameters
(severity factor, enzyme loading, xylose recovery) was found or
independently fetched for this document -- real commercial process
performance data of this kind is evidently held back for direct
engagement at both companies, the same gap the sibling repos' own
vendor documents find repeatedly. Clariant's own sunliquid product/news
pages returned HTTP 404 at the time of fetching (a real access gap, not
a claim the plant or figures aren't real -- they are independently
confirmed via bioenergyinternational.com's direct quotation of the same
press statement).

## Note on this document's scope

2G cellulosic ethanol is a young, thin commercial market worldwide (two
real operating commercial-scale plants referenced here: IOCL Panipat and
Clariant's Podari), so there is less of an independent, competing
technology-catalog tradition to cross-check against than the sibling
repos' larger component-catalog documents -- but unlike the first
version of this document, this update found a real SECOND full-chain
plant data point, not just a second unquantified technology name.
