"""
merge_genetics_yield.py

Purpose
-------
Link your existing genetics data (Site_Year_Master.csv) to REAL yield/fruiting
data, once you have it, by matching on (site_id, year).

This script does NOT generate, simulate, or guess any yield values.
It only merges genuine data you provide in a new file: Yield_Data_REAL.csv

How to use
----------
1. When you get real yield/fruiting numbers (from your own sampling, or from
   a source like the Murat email reply), create a file called
   Yield_Data_REAL.csv in this same folder with these columns:

       site_id, year, yield_kg_ha, fruiting_body_count, data_source

   - site_id and year MUST match the values in Site_Year_Master.csv exactly
     (e.g. "PB1", 2011) so rows can be linked correctly.
   - yield_kg_ha and fruiting_body_count: fill in whichever you actually have.
     Leave the other blank (not zero, not estimated) if you don't have it.
   - data_source: a short note on where this number came from
     (e.g. "own field count", "Chen et al. 2021 Table 2", "Murat correspondence").
     This keeps provenance honest and traceable, exactly like Source_Metadata.csv
     already does for your genetics data.

2. Run this script. It will:
   - Load your real genetics table (Site_Year_Master.csv)
   - Load your real yield table (Yield_Data_REAL.csv)
   - Merge them on (site_id, year)
   - Report exactly how many site-years got a real match, and which ones
     are still missing yield data
   - Save the merged result as Site_Year_Merged.csv

3. It will NOT run any model. That's a deliberate separate step, so you
   always check data completeness first before fitting anything.
"""

import pandas as pd
import sys
import os

GENETICS_FILE = "Site_Year_Master.csv"
YIELD_FILE = "Yield_Data_REAL.csv"
OUTPUT_FILE = "Site_Year_Merged.csv"

REQUIRED_YIELD_COLUMNS = ["site_id", "year", "yield_kg_ha", "fruiting_body_count", "data_source"]


def load_genetics():
    if not os.path.exists(GENETICS_FILE):
        sys.exit(f"ERROR: {GENETICS_FILE} not found. Run this script from the folder containing your data.")
    df = pd.read_csv(GENETICS_FILE)
    if "site_id" not in df.columns or "year" not in df.columns:
        sys.exit(f"ERROR: {GENETICS_FILE} must contain 'site_id' and 'year' columns.")
    return df


def load_yield():
    if not os.path.exists(YIELD_FILE):
        print(f"\nNo {YIELD_FILE} found yet.")
        print("Create this file with columns:", REQUIRED_YIELD_COLUMNS)
        print("Fill in only real, measured or properly-cited values. Leave unknowns blank.")
        print("Re-run this script once you have it.\n")
        sys.exit(0)

    df = pd.read_csv(YIELD_FILE)
    missing_cols = [c for c in REQUIRED_YIELD_COLUMNS if c not in df.columns]
    if missing_cols:
        sys.exit(f"ERROR: {YIELD_FILE} is missing required columns: {missing_cols}")
    return df


def main():
    genetics_df = load_genetics()
    yield_df = load_yield()

    print(f"Genetics table: {len(genetics_df)} site-years")
    print(f"Yield table:    {len(yield_df)} rows provided")

    # Warn about any yield rows that don't correspond to a known genetics site-year
    genetics_keys = set(zip(genetics_df["site_id"], genetics_df["year"]))
    yield_keys = set(zip(yield_df["site_id"], yield_df["year"]))

    unmatched_yield_rows = yield_keys - genetics_keys
    if unmatched_yield_rows:
        print("\nWARNING: The following (site_id, year) pairs in your yield file")
        print("do NOT match any row in your genetics table. These will NOT be merged")
        print("in, since they don't correspond to a real site-year you have genetics for:")
        for site, year in sorted(unmatched_yield_rows):
            print(f"   - {site} {year}")

    merged = genetics_df.merge(
        yield_df,
        on=["site_id", "year"],
        how="left",
        suffixes=("", "_yield")
    )

    n_with_yield = merged["yield_kg_ha"].notna().sum() if "yield_kg_ha" in merged.columns else 0
    n_with_fruiting = merged["fruiting_body_count"].notna().sum() if "fruiting_body_count" in merged.columns else 0

    print(f"\nMerge complete.")
    print(f"Site-years with real yield_kg_ha:         {n_with_yield} / {len(genetics_df)}")
    print(f"Site-years with real fruiting_body_count: {n_with_fruiting} / {len(genetics_df)}")

    still_missing = merged[merged["yield_kg_ha"].isna() & merged["fruiting_body_count"].isna()] \
        if "yield_kg_ha" in merged.columns and "fruiting_body_count" in merged.columns else genetics_df

    if len(still_missing) > 0:
        print(f"\nSite-years still missing ANY outcome data ({len(still_missing)}):")
        print(still_missing[["site_id", "year"]].to_string(index=False))

    merged.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved merged table to {OUTPUT_FILE}")
    print("NOTE: This file is only ready for modeling once outcome coverage is sufficient.")
    print("Do not run RF/LOSO analysis on this until real yield/fruiting values exist")
    print("for a meaningful number of site-years (check with the power analysis script).")


if __name__ == "__main__":
    main()
