# Cleaning Log

| Step | Rows before | Rows after | Detail |
|---|---|---|---|
| Load raw data | 30,000 | 30,000 | 25 columns |
| Rename PAY_0 to PAY_1 and the target to 'default' | 30,000 | 30,000 | PAY_1 = September 2005 (most recent), PAY_6 = April 2005 |
| Merge undocumented / unknown codes | 30,000 | 30,000 | EDUCATION 345 rows to 'others' (4); MARRIAGE 54 rows to 'others' (3) |
| Flag duplicate rows (kept) | 30,000 | 30,000 | 70 rows flagged |
| Add behavioural features | 30,000 | 30,000 | max_delay, n_delinquent_months, util_latest, util_avg, pay_to_bill_ratio, bill_trend (negative bills treated as 0 in utilisation; payment ratio capped at 1.5) |