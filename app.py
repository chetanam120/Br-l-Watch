"""
app.py — Brûlé Watch / MycoMate Interactive Methodology Demo

Run locally with:  streamlit run app.py
Deploy free at:     https://share.streamlit.io  or  https://huggingface.co/spaces

This app demonstrates the VALIDATED METHODOLOGY (leakage audit, power
analysis, LOSO framework) using REAL genetic data. It does NOT claim to
predict truffle yield -- that requires real outcome data we don't have yet.
See the "Current Status" section in the app for full transparency.
"""

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Brûlé Watch — Methodology Demo", layout="wide")

# ---------------------------------------------------------------------
# REAL genetic data: 21 site-years, from Taschen et al. 2016 (Molecular
# Ecology, DOI 10.1111/mec.13864), Dryad doi:10.5061/dryad.vm11r.
# These are the ACTUAL mating-type balance values pulled from that
# dataset earlier in this project -- not simulated.
# ---------------------------------------------------------------------
DATA = pd.DataFrame([
    ("PB1", 2011, 0.467), ("PB1", 2012, 0.917), ("PB1", 2013, 0.286),
    ("PB2", 2011, 0.857), ("PB2", 2012, 0.750), ("PB2", 2013, 0.900),
    ("PB3", 1996, 0.615), ("PB3", 1997, 0.500),
    ("PG1", 1995, 1.000), ("PG1", 1996, 0.558), ("PG1", 1997, 0.526),
    ("SB1", 2011, 0.159), ("SB1", 2012, 0.700), ("SB1", 2014, 1.000),
    ("SB2", 2011, 0.909), ("SB2", 2012, 0.800), ("SB2", 2013, 0.667),
    ("SG1", 2013, 0.837), ("SG1", 2014, 0.800),
    ("SG2", 2013, 0.870), ("SG2", 2014, 0.500),
], columns=["site_id", "year", "mating_type_balance_index"])

# ---------------------------------------------------------------------
# HEADER + STATUS BANNER
# ---------------------------------------------------------------------
st.title("🍄 Brûlé Watch — Genetics-Informed Truffle Cultivation")
st.caption("Interactive methodology demo — built on real published genetic data")

st.warning(
    "**What this demo shows:** a validated statistical methodology "
    "(leakage-audit process + power analysis) applied to REAL genetic "
    "data from 21 published site-years.\n\n"
    "**What this demo does NOT show:** a working truffle yield predictor. "
    "We do not yet have real, site-matched yield/production data, so no "
    "yield prediction is made or implied anywhere in this app.",
    icon="⚠️"
)

tab1, tab2, tab3 = st.tabs([
    "📊 Real Genetic Data",
    "🔍 The Leakage Audit (our key finding)",
    "📐 Power Analysis Calculator"
])

# ---------------------------------------------------------------------
# TAB 1: Real data
# ---------------------------------------------------------------------
with tab1:
    st.subheader("21 real site-years of mating-type genetic data")
    st.markdown(
        "Source: Taschen et al. (2016), *Molecular Ecology* 25:5611–5627, "
        "DOI [10.1111/mec.13864](https://doi.org/10.1111/mec.13864). "
        "Data: [Dryad doi:10.5061/dryad.vm11r](https://doi.org/10.5061/dryad.vm11r)."
    )
    st.dataframe(DATA, use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Site-years", len(DATA))
    col2.metric("Mean mating balance", f"{DATA['mating_type_balance_index'].mean():.3f}")
    col3.metric("Sites fully imbalanced (<0.20)",
                int((DATA['mating_type_balance_index'] < 0.20).sum()))

    st.info(
        "Note: MAT1-1 and MAT1-2 presence is 100% (both mating types detected) "
        "at every site-year in this dataset. This is *T. melanosporum*'s real "
        "genetic structure data — it has no linked yield/production values, "
        "so it cannot show a yield prediction. That's exactly the gap this "
        "project is trying to close next (see repo README)."
    )

# ---------------------------------------------------------------------
# TAB 2: The leakage audit story
# ---------------------------------------------------------------------
with tab2:
    st.subheader("How we caught our own data leakage")
    st.markdown("""
An earlier version of our pipeline found that genetics appeared to improve
yield prediction. Before reporting that, we audited *why*.

**What we found:** the apparent effect was driven almost entirely by
`genetic_sample_count` and `diversity_per_sample` — both proxies for how
much sampling effort went into a site, not genetics itself.
""")

    audit_df = pd.DataFrame({
        "Feature": ["genetic_sample_count", "diversity_per_sample",
                    "mating_type_balance_index", "mycorrhization_index"],
        "corr(sample effort)": [1.00, 0.81, -0.06, 0.04],
        "corr(target)": [0.52, 0.41, -0.30, 0.13],
        "Verdict": ["❌ LEAKAGE — removed", "❌ LEAKAGE — removed",
                    "✅ Clean — kept", "✅ Clean — kept"],
    })
    st.dataframe(audit_df, use_container_width=True, hide_index=True)

    st.markdown("""
After removing the two leaking features and re-running the identical
leave-one-site-out (LOSO) cross-validation pipeline, the "genetics helps"
result disappeared — RMSE got slightly *worse* with genetics added
(not statistically significant either direction), and a sensitivity check
excluding the most extreme site confirmed the null.

**We consider this audit-and-correction process — catching a false positive
before reporting it — the most important result of this project so far.**
""")

# ---------------------------------------------------------------------
# TAB 3: Power analysis calculator (live, real formula)
# ---------------------------------------------------------------------
with tab3:
    st.subheader("Why 21 site-years isn't enough — try it yourself")
    st.markdown(
        "This calculator uses the same power-analysis method from our "
        "pipeline (`run_power_analysis.py`). Adjust the sliders to see how "
        "sample size requirements change with effect size."
    )

    r = st.slider("Observed correlation (r) you want to detect", 0.05, 0.60, 0.13, 0.01)
    power = st.slider("Desired statistical power", 0.60, 0.95, 0.80, 0.05)
    alpha = st.select_slider("Significance level (alpha)", options=[0.01, 0.05, 0.10], value=0.05)

    # Standard sample size formula for detecting a correlation (Fisher z-approximation)
    from scipy.stats import norm
    z_alpha = norm.ppf(1 - alpha / 2)
    z_power = norm.ppf(power)
    z_r = 0.5 * np.log((1 + r) / (1 - r))  # Fisher z-transform
    n_required = ((z_alpha + z_power) / z_r) ** 2 + 3

    col1, col2 = st.columns(2)
    col1.metric("Site-years required", f"{int(np.ceil(n_required))}")
    col2.metric("Your current N", "21", delta=f"{21 - int(np.ceil(n_required))}", delta_color="inverse")

    if n_required > 21:
        st.error(
            f"At r={r}, you'd need ~{int(np.ceil(n_required))} site-years to "
            f"reliably detect this effect. Your current N=21 is underpowered "
            f"for effects this small — this is *why* the null result is "
            f"honest, not necessarily evidence of zero effect."
        )
    else:
        st.success(
            f"At r={r}, N=21 would be sufficient to detect this effect "
            f"reliably."
        )

# ---------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------
st.divider()
st.markdown("""
**Current status:** methodology validated on real genetic data.
Real, site-matched yield/fruiting outcome data is still needed before any
predictive claim can be made — see the
[project repository](https://github.com/chetanam120/fortyguard-truffle-genetics)
for full details, code, and next steps.
""")
