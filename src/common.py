"""Column definitions shared by several scripts."""
PAY_RAW = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]   # source naming (there is no PAY_1)
PAY_COLS = [f"PAY_{i}" for i in range(1, 7)]                        # renamed consistently in cleaning
BILL_COLS = [f"BILL_AMT{i}" for i in range(1, 7)]
PAYAMT_COLS = [f"PAY_AMT{i}" for i in range(1, 7)]
TARGET_RAW = "default payment next month"
TARGET = "default"
# Demographic attributes kept in the cleaned data for auditing only. They are NOT used as model
# features, because using them in lending decisions is generally not permitted.
EXCLUDED_FROM_MODEL = ["SEX", "EDUCATION", "MARRIAGE", "AGE"]
