# Model Metrics (hold-out test set)

Train 21,000 accounts, test 9,000; default rate 22.12%; seed 42.
Features: 25 account-behaviour variables. Excluded: SEX, EDUCATION, MARRIAGE, AGE.

| Model | AUC | PR-AUC | KS | Brier | 5-fold CV AUC (train) |
|---|---|---|---|---|---|
| logistic | 0.7531 | 0.5037 | 0.3955 | 0.1420 | 0.7604 +/- 0.0106 |
| gradient_boosting | 0.7780 | 0.5521 | 0.4179 | 0.1357 | 0.7855 +/- 0.0103 |

One-variable baselines (test AUC): latest repayment status 0.6833; worst delay in 6 months 0.7046

## Calibration, logistic (risk bands, 1 = lowest risk)

|   band |   accounts |   mean_predicted |   actual_default_rate |
|-------:|-----------:|-----------------:|----------------------:|
|      1 |        900 |           0.0627 |                0.0533 |
|      2 |        900 |           0.093  |                0.0889 |
|      3 |        900 |           0.1078 |                0.1111 |
|      4 |        900 |           0.1195 |                0.13   |
|      5 |        900 |           0.1298 |                0.1456 |
|      6 |        900 |           0.1399 |                0.1689 |
|      7 |        900 |           0.1735 |                0.18   |
|      8 |        900 |           0.2953 |                0.26   |
|      9 |        900 |           0.4295 |                0.4333 |
|     10 |        900 |           0.6501 |                0.6411 |

## Calibration, gradient boosting

|   band |   accounts |   mean_predicted |   actual_default_rate |
|-------:|-----------:|-----------------:|----------------------:|
|      1 |        900 |           0.0518 |                0.04   |
|      2 |        900 |           0.0706 |                0.0578 |
|      3 |        900 |           0.0917 |                0.0944 |
|      4 |        900 |           0.1155 |                0.1178 |
|      5 |        900 |           0.1374 |                0.1722 |
|      6 |        900 |           0.1609 |                0.1756 |
|      7 |        900 |           0.1925 |                0.1756 |
|      8 |        900 |           0.2665 |                0.2622 |
|      9 |        900 |           0.4072 |                0.43   |
|     10 |        900 |           0.7023 |                0.6867 |

## Largest logistic coefficients (standardised features)

|                     |      0 |
|:--------------------|-------:|
| n_delinquent_months |  0.65  |
| max_delay           |  0.361 |
| PAY_1               |  0.247 |
| PAY_AMT2            | -0.2   |
| LIMIT_BAL           | -0.187 |
| BILL_AMT3           |  0.133 |
| PAY_3               | -0.124 |
| PAY_AMT1            | -0.113 |
| PAY_6               | -0.108 |
| PAY_2               | -0.104 |