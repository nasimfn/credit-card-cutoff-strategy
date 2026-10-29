"""
Step 7: Build the data dictionary for data/processed/clean.csv and data/processed/scored_test.csv.

Descriptions are written by hand. Types and blank rates are computed from the files, and the
script stops with an error if a column has no description (or a description has no column).

Output: docs/data_dictionary.csv, docs/data_dictionary.md
"""
from pathlib import Path

import pandas as pd

OUT = Path("docs")
UCI = "UCI dataset (Yeh, 2009)"
DERIVED = "Derived in this project"
MONTHS = {1: "September 2005", 2: "August 2005", 3: "July 2005", 4: "June 2005", 5: "May 2005", 6: "April 2005"}

CLEAN = {
    "ID": ("Client identifier.", UCI, "Unchanged."),
    "LIMIT_BAL": ("Amount of credit given, in NT dollars; includes individual and family (supplementary) credit.",
                  UCI, "Unchanged."),
    "SEX": ("Sex (1 = male, 2 = female).", UCI,
            "Unchanged. Kept for auditing only; NOT used in the model."),
    "EDUCATION": ("Education (1 = graduate school, 2 = university, 3 = high school, 4 = others).", UCI,
                  "Codes 0, 5 and 6 (345 rows) are not defined by UCI and were merged into 4. NOT used in the model."),
    "MARRIAGE": ("Marital status (1 = married, 2 = single, 3 = others).", UCI,
                 "Code 0 (54 rows) is not defined and was merged into 3. NOT used in the model."),
    "AGE": ("Age in years.", UCI, "Unchanged. Kept for auditing only; NOT used in the model."),
    "default": ("Whether the client defaulted on the payment the following month (1 = yes, 0 = no). "
                "This is the outcome being predicted.", UCI,
                "Renamed from 'default payment next month'. In SQL tables it is called 'defaulted' because "
                "'default' is a reserved word."),
    "dup_flag": ("True if another row has identical values in every field except ID.", DERIVED,
                 "Flag only; the 70 rows (35 pairs) were kept."),
    "max_delay": ("Worst repayment delay in months across the six months, with 0 for no delay.", DERIVED,
                  "max(PAY_1..PAY_6, 0). Codes -2 and -1 count as no delay."),
    "n_delinquent_months": ("Number of the six months in which payment was at least one month late.", DERIVED,
                            "Count of PAY_1..PAY_6 >= 1."),
    "util_latest": ("Latest bill as a share of the credit limit (credit utilisation).", DERIVED,
                    "max(BILL_AMT1, 0) / LIMIT_BAL. Can exceed 1 for over-limit accounts."),
    "util_avg": ("Average of the six bills as a share of the credit limit.", DERIVED,
                 "mean(max(BILL_AMT1..6, 0)) / LIMIT_BAL."),
    "pay_to_bill_ratio": ("Total paid over the six months divided by total billed.", DERIVED,
                          "sum(PAY_AMT1..6) / sum(max(BILL_AMT, 0)); capped at 1.5; set to 1 when nothing was billed."),
    "bill_trend": ("Change in the bill from April to September as a share of the credit limit.", DERIVED,
                   "(BILL_AMT1 - BILL_AMT6) / LIMIT_BAL."),
}
for i, month in MONTHS.items():
    CLEAN[f"PAY_{i}"] = (
        f"Repayment status in {month}. Documented codes: -1 = paid duly, 1 to 8 = delay of that many months, "
        f"9 = nine months or more.", UCI,
        "Codes -2 and 0 are NOT defined by UCI and were kept as published. A common reading is -2 = no "
        "consumption and 0 = revolving credit, but that is an assumption." +
        (" Renamed from PAY_0 (the source has no PAY_1)." if i == 1 else ""))
    CLEAN[f"BILL_AMT{i}"] = (f"Amount of bill statement in {month}, in NT dollars.", UCI,
                             "Unchanged. Negative values (credit balances) were kept.")
    CLEAN[f"PAY_AMT{i}"] = (f"Amount paid in {month}, in NT dollars.", UCI, "Unchanged.")

SCORED = {k: CLEAN[k] for k in ["ID", "default", "LIMIT_BAL", "SEX", "AGE", "EDUCATION", "MARRIAGE", "PAY_1",
                                "max_delay", "util_latest", "BILL_AMT1"]}
SCORED["p_logistic"] = ("Predicted probability of default from the logistic regression.", DERIVED,
                        "Hold-out accounts only (9,000, a stratified 30% split, seed 42).")
SCORED["p_gbm"] = ("Predicted probability of default from the gradient boosting model.", DERIVED,
                   "Hold-out accounts only. This is the score used in the strategy simulation.")


def build(path, spec):
    df = pd.read_csv(path)
    missing, extra = set(df.columns) - set(spec), set(spec) - set(df.columns)
    if missing or extra:
        raise SystemExit(f"{path.name}: undocumented {sorted(missing)}; no column for {sorted(extra)}")
    rows = []
    for c in df.columns:
        desc, src, note = spec[c]
        dtype = "boolean" if df[c].dtype == bool else ("decimal" if df[c].dtype.kind == "f" else "integer")
        rows.append({"file": path.name, "field": c, "type": dtype, "description": desc, "source": src,
                     "notes": note, "pct_blank": round(df[c].isna().mean() * 100, 1)})
    return pd.DataFrame(rows), len(df)


def main():
    OUT.mkdir(exist_ok=True)
    clean, n1 = build(Path("data/processed/clean.csv"), CLEAN)
    scored, n2 = build(Path("data/processed/scored_test.csv"), SCORED)
    out = pd.concat([clean, scored], ignore_index=True)
    out.to_csv(OUT / "data_dictionary.csv", index=False)
    lines = ["# Data Dictionary", "",
             "Source data: Yeh, I. (2009). Default of Credit Card Clients [Dataset]. UCI Machine Learning "
             "Repository. https://doi.org/10.24432/C55S3H (CC BY 4.0).", ""]
    for name, tbl, n in [("clean.csv", clean, n1), ("scored_test.csv", scored, n2)]:
        lines += [f"## data/processed/{name} ({n:,} rows, {len(tbl)} columns)", "",
                  "| Field | Type | Description | Source | Notes | % blank |", "|---|---|---|---|---|---|"]
        for r in tbl.itertuples():
            lines.append(f"| `{r.field}` | {r.type} | {r.description} | {r.source} | {r.notes} | {r.pct_blank} |")
        lines.append("")
    (OUT / "data_dictionary.md").write_text("\n".join(lines))
    print(f"Documented {len(clean)} fields in clean.csv and {len(scored)} in scored_test.csv")


if __name__ == "__main__":
    main()
