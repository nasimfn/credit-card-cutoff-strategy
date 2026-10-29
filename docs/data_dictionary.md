# Data Dictionary

Source data: Yeh, I. (2009). Default of Credit Card Clients [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C55S3H (CC BY 4.0).

## data/processed/clean.csv (30,000 rows, 32 columns)

| Field | Type | Description | Source | Notes | % blank |
|---|---|---|---|---|---|
| `ID` | integer | Client identifier. | UCI dataset (Yeh, 2009) | Unchanged. | 0.0 |
| `LIMIT_BAL` | integer | Amount of credit given, in NT dollars; includes individual and family (supplementary) credit. | UCI dataset (Yeh, 2009) | Unchanged. | 0.0 |
| `SEX` | integer | Sex (1 = male, 2 = female). | UCI dataset (Yeh, 2009) | Unchanged. Kept for auditing only; NOT used in the model. | 0.0 |
| `EDUCATION` | integer | Education (1 = graduate school, 2 = university, 3 = high school, 4 = others). | UCI dataset (Yeh, 2009) | Codes 0, 5 and 6 (345 rows) are not defined by UCI and were merged into 4. NOT used in the model. | 0.0 |
| `MARRIAGE` | integer | Marital status (1 = married, 2 = single, 3 = others). | UCI dataset (Yeh, 2009) | Code 0 (54 rows) is not defined and was merged into 3. NOT used in the model. | 0.0 |
| `AGE` | integer | Age in years. | UCI dataset (Yeh, 2009) | Unchanged. Kept for auditing only; NOT used in the model. | 0.0 |
| `PAY_1` | integer | Repayment status in September 2005. Documented codes: -1 = paid duly, 1 to 8 = delay of that many months, 9 = nine months or more. | UCI dataset (Yeh, 2009) | Codes -2 and 0 are NOT defined by UCI and were kept as published. A common reading is -2 = no consumption and 0 = revolving credit, but that is an assumption. Renamed from PAY_0 (the source has no PAY_1). | 0.0 |
| `PAY_2` | integer | Repayment status in August 2005. Documented codes: -1 = paid duly, 1 to 8 = delay of that many months, 9 = nine months or more. | UCI dataset (Yeh, 2009) | Codes -2 and 0 are NOT defined by UCI and were kept as published. A common reading is -2 = no consumption and 0 = revolving credit, but that is an assumption. | 0.0 |
| `PAY_3` | integer | Repayment status in July 2005. Documented codes: -1 = paid duly, 1 to 8 = delay of that many months, 9 = nine months or more. | UCI dataset (Yeh, 2009) | Codes -2 and 0 are NOT defined by UCI and were kept as published. A common reading is -2 = no consumption and 0 = revolving credit, but that is an assumption. | 0.0 |
| `PAY_4` | integer | Repayment status in June 2005. Documented codes: -1 = paid duly, 1 to 8 = delay of that many months, 9 = nine months or more. | UCI dataset (Yeh, 2009) | Codes -2 and 0 are NOT defined by UCI and were kept as published. A common reading is -2 = no consumption and 0 = revolving credit, but that is an assumption. | 0.0 |
| `PAY_5` | integer | Repayment status in May 2005. Documented codes: -1 = paid duly, 1 to 8 = delay of that many months, 9 = nine months or more. | UCI dataset (Yeh, 2009) | Codes -2 and 0 are NOT defined by UCI and were kept as published. A common reading is -2 = no consumption and 0 = revolving credit, but that is an assumption. | 0.0 |
| `PAY_6` | integer | Repayment status in April 2005. Documented codes: -1 = paid duly, 1 to 8 = delay of that many months, 9 = nine months or more. | UCI dataset (Yeh, 2009) | Codes -2 and 0 are NOT defined by UCI and were kept as published. A common reading is -2 = no consumption and 0 = revolving credit, but that is an assumption. | 0.0 |
| `BILL_AMT1` | integer | Amount of bill statement in September 2005, in NT dollars. | UCI dataset (Yeh, 2009) | Unchanged. Negative values (credit balances) were kept. | 0.0 |
| `BILL_AMT2` | integer | Amount of bill statement in August 2005, in NT dollars. | UCI dataset (Yeh, 2009) | Unchanged. Negative values (credit balances) were kept. | 0.0 |
| `BILL_AMT3` | integer | Amount of bill statement in July 2005, in NT dollars. | UCI dataset (Yeh, 2009) | Unchanged. Negative values (credit balances) were kept. | 0.0 |
| `BILL_AMT4` | integer | Amount of bill statement in June 2005, in NT dollars. | UCI dataset (Yeh, 2009) | Unchanged. Negative values (credit balances) were kept. | 0.0 |
| `BILL_AMT5` | integer | Amount of bill statement in May 2005, in NT dollars. | UCI dataset (Yeh, 2009) | Unchanged. Negative values (credit balances) were kept. | 0.0 |
| `BILL_AMT6` | integer | Amount of bill statement in April 2005, in NT dollars. | UCI dataset (Yeh, 2009) | Unchanged. Negative values (credit balances) were kept. | 0.0 |
| `PAY_AMT1` | integer | Amount paid in September 2005, in NT dollars. | UCI dataset (Yeh, 2009) | Unchanged. | 0.0 |
| `PAY_AMT2` | integer | Amount paid in August 2005, in NT dollars. | UCI dataset (Yeh, 2009) | Unchanged. | 0.0 |
| `PAY_AMT3` | integer | Amount paid in July 2005, in NT dollars. | UCI dataset (Yeh, 2009) | Unchanged. | 0.0 |
| `PAY_AMT4` | integer | Amount paid in June 2005, in NT dollars. | UCI dataset (Yeh, 2009) | Unchanged. | 0.0 |
| `PAY_AMT5` | integer | Amount paid in May 2005, in NT dollars. | UCI dataset (Yeh, 2009) | Unchanged. | 0.0 |
| `PAY_AMT6` | integer | Amount paid in April 2005, in NT dollars. | UCI dataset (Yeh, 2009) | Unchanged. | 0.0 |
| `default` | integer | Whether the client defaulted on the payment the following month (1 = yes, 0 = no). This is the outcome being predicted. | UCI dataset (Yeh, 2009) | Renamed from 'default payment next month'. In SQL tables it is called 'defaulted' because 'default' is a reserved word. | 0.0 |
| `dup_flag` | boolean | True if another row has identical values in every field except ID. | Derived in this project | Flag only; the 70 rows (35 pairs) were kept. | 0.0 |
| `max_delay` | integer | Worst repayment delay in months across the six months, with 0 for no delay. | Derived in this project | max(PAY_1..PAY_6, 0). Codes -2 and -1 count as no delay. | 0.0 |
| `n_delinquent_months` | integer | Number of the six months in which payment was at least one month late. | Derived in this project | Count of PAY_1..PAY_6 >= 1. | 0.0 |
| `util_latest` | decimal | Latest bill as a share of the credit limit (credit utilisation). | Derived in this project | max(BILL_AMT1, 0) / LIMIT_BAL. Can exceed 1 for over-limit accounts. | 0.0 |
| `util_avg` | decimal | Average of the six bills as a share of the credit limit. | Derived in this project | mean(max(BILL_AMT1..6, 0)) / LIMIT_BAL. | 0.0 |
| `pay_to_bill_ratio` | decimal | Total paid over the six months divided by total billed. | Derived in this project | sum(PAY_AMT1..6) / sum(max(BILL_AMT, 0)); capped at 1.5; set to 1 when nothing was billed. | 0.0 |
| `bill_trend` | decimal | Change in the bill from April to September as a share of the credit limit. | Derived in this project | (BILL_AMT1 - BILL_AMT6) / LIMIT_BAL. | 0.0 |

## data/processed/scored_test.csv (9,000 rows, 13 columns)

| Field | Type | Description | Source | Notes | % blank |
|---|---|---|---|---|---|
| `ID` | integer | Client identifier. | UCI dataset (Yeh, 2009) | Unchanged. | 0.0 |
| `default` | integer | Whether the client defaulted on the payment the following month (1 = yes, 0 = no). This is the outcome being predicted. | UCI dataset (Yeh, 2009) | Renamed from 'default payment next month'. In SQL tables it is called 'defaulted' because 'default' is a reserved word. | 0.0 |
| `LIMIT_BAL` | integer | Amount of credit given, in NT dollars; includes individual and family (supplementary) credit. | UCI dataset (Yeh, 2009) | Unchanged. | 0.0 |
| `SEX` | integer | Sex (1 = male, 2 = female). | UCI dataset (Yeh, 2009) | Unchanged. Kept for auditing only; NOT used in the model. | 0.0 |
| `AGE` | integer | Age in years. | UCI dataset (Yeh, 2009) | Unchanged. Kept for auditing only; NOT used in the model. | 0.0 |
| `EDUCATION` | integer | Education (1 = graduate school, 2 = university, 3 = high school, 4 = others). | UCI dataset (Yeh, 2009) | Codes 0, 5 and 6 (345 rows) are not defined by UCI and were merged into 4. NOT used in the model. | 0.0 |
| `MARRIAGE` | integer | Marital status (1 = married, 2 = single, 3 = others). | UCI dataset (Yeh, 2009) | Code 0 (54 rows) is not defined and was merged into 3. NOT used in the model. | 0.0 |
| `PAY_1` | integer | Repayment status in September 2005. Documented codes: -1 = paid duly, 1 to 8 = delay of that many months, 9 = nine months or more. | UCI dataset (Yeh, 2009) | Codes -2 and 0 are NOT defined by UCI and were kept as published. A common reading is -2 = no consumption and 0 = revolving credit, but that is an assumption. Renamed from PAY_0 (the source has no PAY_1). | 0.0 |
| `max_delay` | integer | Worst repayment delay in months across the six months, with 0 for no delay. | Derived in this project | max(PAY_1..PAY_6, 0). Codes -2 and -1 count as no delay. | 0.0 |
| `util_latest` | decimal | Latest bill as a share of the credit limit (credit utilisation). | Derived in this project | max(BILL_AMT1, 0) / LIMIT_BAL. Can exceed 1 for over-limit accounts. | 0.0 |
| `BILL_AMT1` | integer | Amount of bill statement in September 2005, in NT dollars. | UCI dataset (Yeh, 2009) | Unchanged. Negative values (credit balances) were kept. | 0.0 |
| `p_logistic` | decimal | Predicted probability of default from the logistic regression. | Derived in this project | Hold-out accounts only (9,000, a stratified 30% split, seed 42). | 0.0 |
| `p_gbm` | decimal | Predicted probability of default from the gradient boosting model. | Derived in this project | Hold-out accounts only. This is the score used in the strategy simulation. | 0.0 |
