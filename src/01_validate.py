"""
Step 1: Data quality validation on the RAW data. Nothing is modified here.

Each check is a named rule. Results go to reports/qa_summary.md (one row per check) and
reports/qa_issues.csv (one row per failing record, for checks with at most 2,000 failures).

Severity: ERROR = invalid value; WARNING = undocumented or suspicious; INFO = a documented
characteristic of the data that users should know about.
"""
from pathlib import Path

import pandas as pd

from common import PAY_RAW, BILL_COLS, PAYAMT_COLS, TARGET_RAW

IN_FILE = Path("data/raw/default_of_credit_card_clients.csv")
SUMMARY = Path("reports/qa_summary.md")
ISSUES = Path("reports/qa_issues.csv")

EXPECTED_COLUMNS = (["ID", "LIMIT_BAL", "SEX", "EDUCATION", "MARRIAGE", "AGE"] + PAY_RAW + BILL_COLS
                    + PAYAMT_COLS + [TARGET_RAW])
# Codes defined in UCI's published variable description (EDUCATION 1-4 only; repayment status -1 and 1-9)
DOCUMENTED = {"SEX": {1, 2}, "EDUCATION": {1, 2, 3, 4}, "MARRIAGE": {1, 2, 3},
              "PAY": {-1, 1, 2, 3, 4, 5, 6, 7, 8, 9}}

checks, issues = [], []


def record(cid, desc, sev, mask, df, col=None, note=""):
    n = int(mask.sum())
    checks.append((cid, desc, sev, n, note))
    if n and n <= 2000:
        for i in df.index[mask]:
            issues.append({"check_id": cid, "ID": int(df.at[i, "ID"]), "column": col or "",
                           "value": df.at[i, col] if col else ""})


def main():
    df = pd.read_csv(IN_FILE)

    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    extra = [c for c in df.columns if c not in EXPECTED_COLUMNS]
    checks.append(("V01", "All 25 expected columns present, no extras", "ERROR", len(missing) + len(extra),
                   f"missing={missing} extra={extra}"))
    if missing:
        raise SystemExit(f"Missing columns: {missing}")

    record("V02", "ID is unique", "ERROR", df["ID"].duplicated(keep=False), df)
    checks.append(("V03", "No missing values", "ERROR", int(df.isna().sum().sum()), ""))
    record("V04", "Target is 0 or 1", "ERROR", ~df[TARGET_RAW].isin([0, 1]), df, TARGET_RAW)
    record("V05", "Duplicate rows (all fields except ID)", "WARNING",
           df.drop(columns="ID").duplicated(keep=False), df,
           note="70 rows = 35 pairs. Two clients can legitimately share all values; kept and flagged, not removed.")
    record("V06", "LIMIT_BAL is positive", "ERROR", df["LIMIT_BAL"] <= 0, df, "LIMIT_BAL")
    record("V07", "AGE between 18 and 100", "ERROR", ~df["AGE"].between(18, 100), df, "AGE")

    for col in ("SEX", "EDUCATION", "MARRIAGE"):
        bad = ~df[col].isin(DOCUMENTED[col])
        record("V08", f"{col} uses only documented codes", "WARNING", bad, df, col,
               note=f"undocumented values: {sorted(df.loc[bad, col].unique().tolist())}")
    # The Kaggle version of the codebook labels EDUCATION 5 and 6 'unknown'; UCI does not define them.
    checks.append(("V09", "EDUCATION coded 5 or 6 (labelled 'unknown' by Kaggle, undefined by UCI)", "INFO",
                   int(df["EDUCATION"].isin([5, 6]).sum()), "included in V08; the label comes from a secondary source"))

    for col in PAY_RAW:
        bad = ~df[col].isin(DOCUMENTED["PAY"])
        undocumented = sorted(df.loc[bad, col].unique().tolist())
        checks.append(("V10", f"{col} uses only documented codes", "WARNING", int(bad.sum()),
                       f"undocumented values {undocumented}; the codebook does not define them"))

    record("V11", "Payment amounts are non-negative", "ERROR", (df[PAYAMT_COLS] < 0).any(axis=1), df)
    checks.append(("V12", "Rows with a negative bill amount (credit balance)", "INFO",
                   int((df[BILL_COLS] < 0).any(axis=1).sum()), "plausible: overpayment or refund"))
    checks.append(("V13", "Rows where a bill exceeds the credit limit", "INFO",
                   int(df[BILL_COLS].gt(df["LIMIT_BAL"], axis=0).any(axis=1).sum()),
                   "plausible: over-limit accounts"))

    share1 = {c: round((df[c] == 1).mean() * 100, 2) for c in PAY_RAW}
    rare = [c for c in PAY_RAW[1:] if share1[c] < 1 and share1["PAY_0"] > 10]
    checks.append(("V14", "Code 1 (one-month delay) is similarly common in every month", "WARNING", len(rare),
                   f"share of accounts coded 1: {share1}. Cause unknown; coding may differ by month."))

    # Counterintuitive ordering: 'paid duly' (-1) defaulting more than 'revolving' (0)
    rate = df.groupby("PAY_0")[TARGET_RAW].mean()
    checks.append(("V15", "Default rate rises with repayment status (PAY_0: -1 vs 0)", "INFO",
                   int(rate[-1] > rate[0]),
                   f"default rate: PAY_0=-1 {rate[-1]:.1%}, PAY_0=0 {rate[0]:.1%}. Status codes are not strictly ordered."))

    summary = pd.DataFrame(checks, columns=["id", "description", "severity", "n_failures", "note"])
    SUMMARY.parent.mkdir(exist_ok=True)
    pd.DataFrame(issues).to_csv(ISSUES, index=False)
    lines = ["# Data Quality Summary", "",
             f"- Records checked: **{len(df):,}** (clients), **{df.shape[1]}** columns",
             f"- Default rate: **{df[TARGET_RAW].mean():.2%}** ({int(df[TARGET_RAW].sum()):,} defaults)",
             f"- Checks run: **{len(summary)}**; checks with failures: **{(summary.n_failures > 0).sum()}**", "",
             "| Check | Description | Severity | Failures | Note |", "|---|---|---|---|---|"]
    for r in summary.itertuples():
        lines.append(f"| {r.id} | {r.description} | {r.severity} | {r.n_failures:,} | {r.note} |")
    SUMMARY.write_text("\n".join(lines))
    print(summary[summary.n_failures > 0][["id", "description", "severity", "n_failures"]].to_string(index=False))
    print(f"\nSaved {SUMMARY} and {ISSUES} ({len(issues):,} record-level rows)")


if __name__ == "__main__":
    main()
