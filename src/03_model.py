"""
Step 3: Risk models and validation.

Models: logistic regression (interpretable baseline) and gradient boosting (comparison),
both trained on account behaviour only. SEX, EDUCATION, MARRIAGE and AGE are excluded.
A one-variable baseline (latest repayment status) shows how much the models really add.

Input : data/processed/clean.csv
Output: data/processed/scored_test.csv, reports/model_metrics.md, reports/model_metrics.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from common import PAY_COLS, BILL_COLS, PAYAMT_COLS, TARGET, EXCLUDED_FROM_MODEL

IN_FILE = Path("data/processed/clean.csv")
SCORED = Path("data/processed/scored_test.csv")
METRICS_MD = Path("reports/model_metrics.md")
METRICS_JSON = Path("reports/model_metrics.json")

SEED = 42
TEST_SIZE = 0.30
FEATURES = (["LIMIT_BAL"] + PAY_COLS + BILL_COLS + PAYAMT_COLS +
            ["max_delay", "n_delinquent_months", "util_latest", "util_avg", "pay_to_bill_ratio", "bill_trend"])
assert not set(FEATURES) & set(EXCLUDED_FROM_MODEL), "excluded attribute found in features"


def ks_stat(y, p):
    fpr, tpr, _ = roc_curve(y, p)
    return float(np.max(tpr - fpr))


def evaluate(y, p):
    return {"auc": float(roc_auc_score(y, p)), "pr_auc": float(average_precision_score(y, p)),
            "ks": ks_stat(y, p), "brier": float(brier_score_loss(y, p))}


def calibration_table(y, p, bins=10):
    d = pd.DataFrame({"y": y.values, "p": p})
    d["band"] = pd.qcut(d["p"].rank(method="first"), bins, labels=range(1, bins + 1))
    t = d.groupby("band", observed=True).agg(accounts=("y", "size"), mean_predicted=("p", "mean"),
                                             actual_default_rate=("y", "mean")).reset_index()
    return t.round(4)


def main():
    df = pd.read_csv(IN_FILE)
    X, y = df[FEATURES], df[TARGET]
    X_tr, X_te, y_tr, y_te, id_tr, id_te = train_test_split(
        X, y, df.index, test_size=TEST_SIZE, stratify=y, random_state=SEED)
    print(f"train {len(X_tr):,} | test {len(X_te):,} | default rate train {y_tr.mean():.2%} test {y_te.mean():.2%}")

    logit = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
    hgb = HistGradientBoostingClassifier(max_depth=4, learning_rate=0.05, max_iter=300, random_state=SEED)
    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)

    results, probs = {}, {}
    for name, model in [("logistic", logit), ("gradient_boosting", hgb)]:
        cv_auc = cross_val_score(model, X_tr, y_tr, cv=cv, scoring="roc_auc")
        model.fit(X_tr, y_tr)
        p = model.predict_proba(X_te)[:, 1]
        probs[name] = p
        results[name] = {**evaluate(y_te, p), "cv_auc_mean": float(cv_auc.mean()), "cv_auc_std": float(cv_auc.std())}

    # One-variable baselines (a higher repayment status means a higher risk score)
    results["baseline_latest_repayment_status"] = {"auc": float(roc_auc_score(y_te, X_te["PAY_1"]))}
    results["baseline_max_delay"] = {"auc": float(roc_auc_score(y_te, X_te["max_delay"]))}

    # Logistic coefficients (standardised features), to see what drives the score
    coefs = pd.Series(logit.named_steps["logisticregression"].coef_[0], index=FEATURES).sort_values(key=abs, ascending=False)

    out = df.loc[id_te, ["ID", TARGET, "LIMIT_BAL", "SEX", "AGE", "EDUCATION", "MARRIAGE", "PAY_1", "max_delay",
                         "util_latest", "BILL_AMT1"]].copy()
    out["p_logistic"], out["p_gbm"] = probs["logistic"], probs["gradient_boosting"]
    out.to_csv(SCORED, index=False)

    cal_l = calibration_table(y_te, probs["logistic"])
    cal_g = calibration_table(y_te, probs["gradient_boosting"])
    METRICS_JSON.write_text(json.dumps({"settings": {"seed": SEED, "test_size": TEST_SIZE, "features": FEATURES},
                                        "results": results}, indent=2))

    lines = ["# Model Metrics (hold-out test set)", "",
             f"Train {len(X_tr):,} accounts, test {len(X_te):,}; default rate {y.mean():.2%}; seed {SEED}.",
             f"Features: {len(FEATURES)} account-behaviour variables. Excluded: {', '.join(EXCLUDED_FROM_MODEL)}.", "",
             "| Model | AUC | PR-AUC | KS | Brier | 5-fold CV AUC (train) |", "|---|---|---|---|---|---|"]
    for k in ("logistic", "gradient_boosting"):
        r = results[k]
        lines.append(f"| {k} | {r['auc']:.4f} | {r['pr_auc']:.4f} | {r['ks']:.4f} | {r['brier']:.4f} | "
                     f"{r['cv_auc_mean']:.4f} +/- {r['cv_auc_std']:.4f} |")
    lines += ["", f"One-variable baselines (test AUC): latest repayment status "
                  f"{results['baseline_latest_repayment_status']['auc']:.4f}; "
                  f"worst delay in 6 months {results['baseline_max_delay']['auc']:.4f}", "",
              "## Calibration, logistic (risk bands, 1 = lowest risk)", "", cal_l.to_markdown(index=False), "",
              "## Calibration, gradient boosting", "", cal_g.to_markdown(index=False), "",
              "## Largest logistic coefficients (standardised features)", "", coefs.head(10).round(3).to_markdown()]
    METRICS_MD.write_text("\n".join(lines))
    print(pd.DataFrame(results).T.round(4).to_string())
    print("\nTop coefficients:\n", coefs.head(8).round(3).to_string())
    print("\nCalibration (logistic):\n", cal_l.to_string(index=False))


if __name__ == "__main__":
    main()
