# MycoMate: Genetics-Informed Truffle Cultivation — Prediction Pipeline

## Overview

MycoMate investigates whether genetic mating-type structure (*Tuber melanosporum*
heterothallism) can help predict or guide truffle orchard productivity, with the
long-term goal of enabling precision management (e.g. targeted spore trap
placement) instead of uniform, wasteful application across an orchard.

This repository contains a **validated statistical/ML methodology**, developed
and stress-tested on a real published genetic dataset. It is explicitly **not**
a finished yield predictor yet — see "Current Status" below for exactly what
is and isn't proven.

## What's in this repo

- `merge_genetics_yield.py` — merges genetics data with real yield/fruiting
  data by `(site_id, year)`, once such data is available. Refuses to run on
  placeholder or mismatched data; flags any (site, year) pairs that don't
  correspond to a real linked site-year.
- `Yield_Data_TEMPLATE.csv` — template showing the exact format needed for
  real outcome data, with a clearly marked example row (not real data).
- `run_power_analysis.py` — statistical power analysis: given a dataset of
  N site-years and an observed effect size, computes the minimum detectable
  correlation and the N required to detect the observed effect reliably.
- `extract_ssr.py` — extracts richer genetic features (expected heterozygosity,
  per-locus allele diversity, clonal richness) from raw SSR genotype data,
  and runs a leakage audit on each new feature before use.
- (add your LOSO cross-validation / RF training script here if included)

## Methodology highlights

- **Leave-one-site-out (LOSO) cross-validation** — avoids inflated performance
  estimates from random splits on small, clustered orchard data.
- **Leakage audit** — every candidate feature is checked for correlation with
  sampling-effort proxies (e.g. number of genetic samples collected per site)
  before being trusted, since sampling effort can create spurious correlations
  with any target variable.
- **Paired significance testing** (Wilcoxon) and **sensitivity analysis**
  (leave-out of high-leverage sites) — used to confirm whether an observed
  effect (or null result) is robust, not an artifact of one influential site.

### A note on our own process (we think this is the most important part)

An earlier version of this pipeline found that genetic sample count and
diversity-per-sample — both proxies for *how much sampling effort* went into
a site, not genetics itself — were driving an apparent "genetics improves
prediction" result. We audited this, identified it as leakage, removed the
leaking features, and re-ran the full pipeline. The corrected result was a
clean null (no detectable effect at current sample size). We consider this
audit-and-correction process, done before any external claim was made, the
most rigorous and important part of this project so far.

## Current status — what is and isn't proven

**Proven / validated:**
- The LOSO + leakage-audit + significance-testing methodology, run against
  real genetic data (SSR microsatellite genotypes, mating-type presence,
  from a published dataset — see Data Sources below).
- Statistical power analysis showing the sample size needed to reliably
  detect small effect sizes in this kind of data.

**Not yet proven:**
- Any claim that genetics (or genetics + microclimate) predicts real truffle
  yield or fruiting success. This requires a real, matched outcome variable
  (yield_kg_ha or fruiting_body_count) for the same site-years as the genetic
  data — which we do not currently have. Prior internal test runs used a
  placeholder/simulated target column and **do not represent real results**;
  those numbers should not be cited or reused.
- Any specific yield-increase or efficiency figure (e.g. "%X improvement") —
  no such figure has been empirically derived from real cultivation data in
  this project.

## Data sources

- Genetic/mating-type data: Taschen E, Rousset F, Sauve M, Benoit L,
  Richard F, Selosse MA (2016). "How the truffle got its mate: insights
  from genetic structure in spontaneous and planted Mediterranean
  populations of *Tuber melanosporum*." *Molecular Ecology* 25:5611–5627.
  DOI: 10.1111/mec.13864. Data: Dryad doi:10.5061/dryad.vm11r.
- This dataset provides genetic structure only — no yield/production data.
  It is used here strictly as a source for developing and testing the
  statistical methodology, not as a stand-in for site-matched yield data.

## Next steps

1. Obtain real, site-matched yield or fruiting-body count data (in progress —
   direct outreach to original research group).
2. Populate `Yield_Data_REAL.csv` (see `Yield_Data_TEMPLATE.csv` for format)
   and run `merge_genetics_yield.py`.
3. Re-run the validated LOSO/power-analysis pipeline against real outcome data.
4. Only then report any predictive performance or effect-size findings.

## License / citation

If you use this methodology, please cite the data sources above. This
repository's code is available for research and educational use.
