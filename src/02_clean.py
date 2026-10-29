"""
Step 2: Clean the data and build features. Every decision is a named setting and is logged.

Input : data/raw/default_of_credit_card_clients.csv
Output: data/processed/clean.csv, reports/cleaning_log.md
"""
from pathlib import Path

import numpy as np
import pandas as pd

from common import PAY_RAW, PAY_COLS, BILL_COLS, PAYAMT_COLS, TARGET_RAW, TARGET

IN_FILE = Path("data/raw/default_of_credit_card_clients.csv")
OUT_FILE = Path("data/processed/clean.csv")
LOG_FILE = Path("reports/cleaning_log.md")

# ------------------------------- DECISIONS -------------------------------------------
# EDUCATION codes 0, 5 and 6 are undocumented or 'unknown'. Merge them into 4 ('others').
MERGE_EDUCATION_UNKNOWN = True
# MARRIAGE code 0 is undocumented. Merge it into 3 ('others').
MERGE_MARRIAGE_UNKNOWN = True
# Repayment status codes -2 and 0 are not defined in the codebook. They are KEPT as published
# (not recoded). A common reading is -2 = no consumption and 0 = revolving credit, but this is
# an assumption and is documented as one.
# Duplicate rows (all fields except ID) are KEPT and flagged, not removed.
# --------------------------------------------------------------------------------------

log = []


def note(step, before, after, detail):
    log.append((step, before, after, detail))


def main():
    df = pd.read_csv(IN_FILE)
    note("Load raw data", len(df), len(df), f"{df.shape[1]} columns")

    # Consistent names: the source skips PAY_1 (September is PAY_0). Rename so months run 1-6.
    df = df.rename(columns={**dict(zip(PAY_RAW, PAY_COLS)), TARGET_RAW: TARGET})
    note("Rename PAY_0 to PAY_1 and the target to 'default'", len(df), len(df),
         "PAY_1 = September 2005 (most recent), PAY_6 = April 2005")

    n_edu = int(df["EDUCATION"].isin([0, 5, 6]).sum())
    if MERGE_EDUCATION_UNKNOWN:
        df.loc[df["EDUCATION"].isin([0, 5, 6]), "EDUCATION"] = 4
    n_mar = int((df["MARRIAGE"] == 0).sum())
    if MERGE_MARRIAGE_UNKNOWN:
        df.loc[df["MARRIAGE"] == 0, "MARRIAGE"] = 3
    note("Merge undocumented / unknown codes", len(df), len(df),
         f"EDUCATION {n_edu} rows to 'others' (4); MARRIAGE {n_mar} rows to 'others' (3)")

    df["dup_flag"] = df.drop(columns="ID").duplicated(keep=False)
    note("Flag duplicate rows (kept)", len(df), len(df), f"{int(df['dup_flag'].sum())} rows flagged")

    # ---- Features built from account behaviour only ----
    pay = df[PAY_COLS]
    bills_pos = df[BILL_COLS].clip(lower=0)
    df["max_delay"] = pay.clip(lower=0).max(axis=1)
    df["n_delinquent_months"] = (pay >= 1).sum(axis=1)
    df["util_latest"] = (bills_pos["BILL_AMT1"] / df["LIMIT_BAL"]).round(4)
    df["util_avg"] = (bills_pos.mean(axis=1) / df["LIMIT_BAL"]).round(4)
    billed = bills_pos.sum(axis=1)
    paid = df[PAYAMT_COLS].sum(axis=1)
    df["pay_to_bill_ratio"] = np.where(billed > 0, (paid / billed.where(billed > 0)).clip(upper=1.5), 1.0).round(4)
    df["bill_trend"] = ((df["BILL_AMT1"] - df["BILL_AMT6"]) / df["LIMIT_BAL"]).round(4)
    note("Add behavioural features", len(df), len(df),
         "max_delay, n_delinquent_months, util_latest, util_avg, pay_to_bill_ratio, bill_trend "
         "(negative bills treated as 0 in utilisation; payment ratio capped at 1.5)")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False)
    lines = ["# Cleaning Log", "", "| Step | Rows before | Rows after | Detail |", "|---|---|---|---|"]
    for s, b, a, d in log:
        lines.append(f"| {s} | {b:,} | {a:,} | {d} |")
    LOG_FILE.write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"\nSaved {OUT_FILE}")


if __name__ == "__main__":
    main()
