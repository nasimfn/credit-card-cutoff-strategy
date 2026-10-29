"""
Step 5: Run the SQL queries in sql/queries.sql (SQLite).

Loads data/processed/scored_test.csv as 'scored' and data/processed/clean.csv as 'accounts'
(the outcome column is renamed 'defaulted', because 'default' is a reserved SQL word),
runs each query (marked '-- name: <name>'), and saves each result to reports/sql/<name>.csv.
"""
import re
import sqlite3
from pathlib import Path

import pandas as pd

QUERIES = Path("sql/queries.sql")
DB = Path("reports/portfolio.db")
OUT_DIR = Path("reports/sql")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DB.unlink(missing_ok=True)
    with sqlite3.connect(DB) as con:
        pd.read_csv("data/processed/scored_test.csv").rename(columns={"default": "defaulted"}).to_sql("scored", con, index=False)
        pd.read_csv("data/processed/clean.csv").rename(columns={"default": "defaulted"}).to_sql("accounts", con, index=False)
        blocks = re.split(r"^-- name: (\w+)\s*$", QUERIES.read_text(), flags=re.M)[1:]
        for name, sql in zip(blocks[0::2], blocks[1::2]):
            result = pd.read_sql_query(sql, con)
            result.to_csv(OUT_DIR / f"{name}.csv", index=False)
            print(f"\n=== {name} ({len(result)} rows) ===")
            print(result.head(12).to_string(index=False))


if __name__ == "__main__":
    main()
