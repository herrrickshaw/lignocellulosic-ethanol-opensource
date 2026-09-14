"""Interactive 2G cellulosic fuel-ethanol biorefinery conceptual sizing tool.

Run with: streamlit run streamlit_app.py

All methods are cited public-domain correlations - see README.md and
docs/METHODOLOGY.md for sources.
"""
from __future__ import annotations

import streamlit as st

from lignocellulosic_ethanol import cofermentation as CF
from lignocellulosic_ethanol import dehydration as DH
from lignocellulosic_ethanol import distillation as D
from lignocellulosic_ethanol import enzymatic_hydrolysis as EH
from lignocellulosic_ethanol import feedstock as F
from lignocellulosic_ethanol import pretreatment as PT

st.set_page_config(page_title="2G Cellulosic Ethanol Conceptual Sizing", layout="wide")
st.title("2G Cellulosic Fuel-Ethanol Biorefinery (open-source)")
st.caption(
    "Independent open-source conceptual sizing using public-domain correlations "
    "(dilute-acid pretreatment, enzymatic hydrolysis, C5+C6 co-fermentation, "
    "Fenske-Underwood-Gilliland) and CoolProp thermodynamics. Not derived from any "
    "proprietary vendor/client data. See README.md and docs/METHODOLOGY.md for citations, "
    "and the disclaimer at the bottom."
)

tab_feed, tab_pre, tab_hyd, tab_ferm, tab_dist, tab_dehy, tab_chain = st.tabs([
    "Feedstock", "Pretreatment", "Enzymatic Hydrolysis", "Co-fermentation",
    "Distillation", "Dehydration", "Full Chain",
])

# ---------------------------------------------------------------------
with tab_feed:
    st.header("Feedstock")
    substrate = st.radio("Substrate", ["Rice straw", "Corn stover", "Bagasse"])
    flow_tpd = st.number_input("Feedstock flow (tonnes/day)", min_value=1.0, value=425.7)
    flow_kg_s = flow_tpd * 1000.0 / 86400.0
    fs = {"Rice straw": F.rice_straw, "Corn stover": F.corn_stover, "Bagasse": F.bagasse}[substrate](flow_kg_s)
    st.session_state["feedstock"] = fs
    colA, colB, colC, colD = st.columns(4)
    colA.metric("Cellulose", f"{fs.cellulose_mass_frac:.0%}")
    colB.metric("Hemicellulose", f"{fs.hemicellulose_mass_frac:.0%}")
    colC.metric("Lignin", f"{fs.lignin_mass_frac:.0%}")
    colD.metric("Ash", f"{fs.ash_mass_frac:.0%}")

# ---------------------------------------------------------------------
with tab_pre:
    st.header("Dilute-acid pretreatment")
    if "feedstock" not in st.session_state:
        st.info("Set up the Feedstock tab first.")
    else:
        fs = st.session_state["feedstock"]
        xylose_recovery = st.slider("Xylose recovery fraction", 0.40, 0.95, PT.DEFAULT_XYLOSE_RECOVERY_FRACTION)
        if st.button("Run pretreatment", type="primary"):
            r = PT.pretreat(fs, xylose_recovery)
            st.session_state["pretreated"] = r
            colA, colB = st.columns(2)
            colA.metric("Xylose produced", f"{r.xylose_produced_kg_s * 86.4:,.1f} t/day")
            colB.metric("Cellulose to hydrolysis", f"{r.cellulose_passthrough_kg_s * 86.4:,.1f} t/day")

# ---------------------------------------------------------------------
with tab_hyd:
    st.header("Enzymatic hydrolysis")
    if "pretreated" not in st.session_state:
        st.info("Run the Pretreatment tab first.")
    else:
        pt = st.session_state["pretreated"]
        cellulose_eff = st.slider("Cellulose conversion efficiency", 0.20, 0.99, EH.DEFAULT_CELLULOSE_CONVERSION_EFFICIENCY)
        if st.button("Run hydrolysis", type="primary"):
            r = EH.hydrolyze_cellulose(pt, cellulose_eff)
            st.session_state["hydrolyzed"] = r
            colA, colB = st.columns(2)
            colA.metric("Glucose produced", f"{r.glucose_produced_kg_s * 86.4:,.1f} t/day")
            colB.metric("Unconverted cellulose", f"{r.unconverted_cellulose_kg_s * 86.4:,.1f} t/day")

            lig = EH.lignin_residue_energy(pt, r, st.session_state["feedstock"])
            st.caption(f"Lignin/residue for process heat: {lig.residue_mass_flow_kg_s * 86.4:,.1f} t/day "
                       f"at {lig.blended_hhv_MJ_kg:.1f} MJ/kg")

# ---------------------------------------------------------------------
with tab_ferm:
    st.header("C5+C6 co-fermentation")
    if "hydrolyzed" not in st.session_state:
        st.info("Run the Enzymatic Hydrolysis tab first.")
    else:
        pt, hy = st.session_state["pretreated"], st.session_state["hydrolyzed"]
        c1, c2 = st.columns(2)
        with c1:
            glucose_eff = st.slider("Glucose fermentation efficiency", 0.50, 1.00, CF.DEFAULT_GLUCOSE_FERMENTATION_EFFICIENCY)
        with c2:
            xylose_eff = st.slider("Xylose fermentation efficiency", 0.30, 1.00, CF.DEFAULT_XYLOSE_FERMENTATION_EFFICIENCY)
        if st.button("Run co-fermentation", type="primary"):
            r = CF.coferment(hy, pt, glucose_eff, xylose_eff)
            st.session_state["coferm"] = r
            colA, colB, colC = st.columns(3)
            colA.metric("Total ethanol", f"{r.total_ethanol_l_s * 86400:,.0f} L/day")
            colB.metric("From glucose", f"{r.ethanol_from_glucose_kg_s / r.total_ethanol_kg_s:.0%}")
            colC.metric("From xylose", f"{r.ethanol_from_xylose_kg_s / r.total_ethanol_kg_s:.0%}")

# ---------------------------------------------------------------------
with tab_dist:
    st.header("Distillation (Fenske-Underwood-Gilliland)")
    if "coferm" not in st.session_state:
        st.info("Run the Co-fermentation tab first.")
    else:
        x_feed = st.slider("Beer/hydrolysate ethanol (%w/w)", 0.01, 0.10, 0.03)
        x_dist = st.slider("Distillate target (%w/w)", 0.70, 0.955, 0.94)
        if st.button("Design column", type="primary"):
            col = D.design_column(x_feed, x_dist, 0.0005)
            st.session_state["column"] = col
            colA, colB, colC = st.columns(3)
            colA.metric("Actual stages", f"{col.n_actual_stages:.0f}")
            colB.metric("Reflux ratio", f"{col.r_actual:.2f}")
            colC.metric("Distillate purity", f"{col.distillate_mass_frac_ethanol:.1%}")

# ---------------------------------------------------------------------
with tab_dehy:
    st.header("Molecular sieve dehydration (3A zeolite VPSA)")
    if "coferm" not in st.session_state or "column" not in st.session_state:
        st.info("Run the Co-fermentation and Distillation tabs first.")
    else:
        r, col = st.session_state["coferm"], st.session_state["column"]
        vapor_kg_s = r.total_ethanol_kg_s / col.distillate_mass_frac_ethanol
        if st.button("Size dehydration bed", type="primary"):
            bed = DH.size_dehydration_bed(vapor_kg_s, 1 - col.distillate_mass_frac_ethanol)
            colA, colB, colC = st.columns(3)
            colA.metric("Bed size", f"{bed.bed_diameter_m:.2f} m dia x {bed.bed_height_m:.1f} m")
            colB.metric("Number of beds", bed.n_beds)
            colC.metric("Meets BIS spec", str(bed.meets_bis_spec))

# ---------------------------------------------------------------------
with tab_chain:
    st.header("Full chain: rice straw -> ethanol")
    st.caption("Runs every module in sequence - see examples/full_chain_worked_example.py.")
    st.markdown(
        "This mirrors the repo's own worked example, run at IOCL Panipat's real, publicly "
        "disclosed scale (425.7 t/day rice straw, published 100 KLPD design capacity). See "
        "`docs/VALIDATION.md` for an honest overshoot the comparison surfaced, and a separate "
        "real operating finding (62% of design throughput, Nov-Dec 2025). Use the individual "
        "tabs above to explore each unit interactively, or run "
        "`python examples/full_chain_worked_example.py` for the full printed trace."
    )

st.divider()
st.caption(
    "**Disclaimer**: this tool implements textbook/public-domain conceptual sizing "
    "methods for early-stage screening only. It is not a substitute for a rigorous "
    "process simulator, enzyme/fermentation kinetics model, or vendor-certified "
    "equipment data for detailed design."
)
