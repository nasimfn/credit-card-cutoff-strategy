# Data Quality Summary

- Records checked: **30,000** (clients), **25** columns
- Default rate: **22.12%** (6,636 defaults)
- Checks run: **22**; checks with failures: **14**

| Check | Description | Severity | Failures | Note |
|---|---|---|---|---|
| V01 | All 25 expected columns present, no extras | ERROR | 0 | missing=[] extra=[] |
| V02 | ID is unique | ERROR | 0 |  |
| V03 | No missing values | ERROR | 0 |  |
| V04 | Target is 0 or 1 | ERROR | 0 |  |
| V05 | Duplicate rows (all fields except ID) | WARNING | 70 | 70 rows = 35 pairs. Two clients can legitimately share all values; kept and flagged, not removed. |
| V06 | LIMIT_BAL is positive | ERROR | 0 |  |
| V07 | AGE between 18 and 100 | ERROR | 0 |  |
| V08 | SEX uses only documented codes | WARNING | 0 | undocumented values: [] |
| V08 | EDUCATION uses only documented codes | WARNING | 345 | undocumented values: [0, 5, 6] |
| V08 | MARRIAGE uses only documented codes | WARNING | 54 | undocumented values: [0] |
| V09 | EDUCATION coded 5 or 6 (labelled 'unknown' by Kaggle, undefined by UCI) | INFO | 331 | included in V08; the label comes from a secondary source |
| V10 | PAY_0 uses only documented codes | WARNING | 17,496 | undocumented values [-2, 0]; the codebook does not define them |
| V10 | PAY_2 uses only documented codes | WARNING | 19,512 | undocumented values [-2, 0]; the codebook does not define them |
| V10 | PAY_3 uses only documented codes | WARNING | 19,849 | undocumented values [-2, 0]; the codebook does not define them |
| V10 | PAY_4 uses only documented codes | WARNING | 20,803 | undocumented values [-2, 0]; the codebook does not define them |
| V10 | PAY_5 uses only documented codes | WARNING | 21,493 | undocumented values [-2, 0]; the codebook does not define them |
| V10 | PAY_6 uses only documented codes | WARNING | 21,181 | undocumented values [-2, 0]; the codebook does not define them |
| V11 | Payment amounts are non-negative | ERROR | 0 |  |
| V12 | Rows with a negative bill amount (credit balance) | INFO | 1,930 | plausible: overpayment or refund |
| V13 | Rows where a bill exceeds the credit limit | INFO | 3,931 | plausible: over-limit accounts |
| V14 | Code 1 (one-month delay) is similarly common in every month | WARNING | 5 | share of accounts coded 1: {'PAY_0': np.float64(12.29), 'PAY_2': np.float64(0.09), 'PAY_3': np.float64(0.01), 'PAY_4': np.float64(0.01), 'PAY_5': np.float64(0.0), 'PAY_6': np.float64(0.0)}. Cause unknown; coding may differ by month. |
| V15 | Default rate rises with repayment status (PAY_0: -1 vs 0) | INFO | 1 | default rate: PAY_0=-1 16.8%, PAY_0=0 12.8%. Status codes are not strictly ordered. |