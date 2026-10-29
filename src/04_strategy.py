"""
Step 4: Strategy simulation, a limit-increase eligibility cutoff for existing cardholders.

Framing (an illustrative assumption, not TD data): an account that is made eligible earns 1 unit
of profit if it stays good and costs X units if it defaults; a declined account earns and costs 0.
X is unknown, so every result is shown for X = 3, 5, 8 and 12.

For a cutoff on predicted default probability p, the break-even rule is: make an account
eligible while p < 1 / (1 + X). The simulation checks that rule against the actual outcomes.

Input : data/processed/scored_test.csv (hold-out accounts, scored by gradient boosting)
Output: reports/strategy/*.csv and reports/strategy_summary.md
"""
from pathlib import Path

import numpy as np
import pandas as pd

IN_FILE = Path("data/processed/scored_test.csv")
OUT_DIR = Path("reports/strategy")
SUMMARY = Path("reports/strategy_summary.md")

SCORE = "p_gbm"
RATIOS = [3, 5, 8, 12]          # X: loss per default, in units of profit per good account
CENTRAL_X = 5
N_BOOT = 300
SEED = 42


def curve(y_sorted, ratios):
    """Cumulative outcomes when approving the k lowest-risk accounts, k = 0..n."""
    n = len(y_sorted)
    k = np.arange(0, n + 1)
    defaults = np.concatenate([[0], np.cumsum(y_sorted)])
    good = k - defaults
    return k, good, defaults, {X: good - X * defaults for X in ratios}


def best_rate(y_sorted, X, grid):
    n = len(y_sorted)
    k, good, defaults, ev = curve(y_sorted, [X])
    idx = np.round(grid * n).astype(int)
    return grid[np.argmax(ev[X][idx])]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(IN_FILE).sort_values(SCORE, kind="mergesort").reset_index(drop=True)
    y = df["default"].to_numpy()
    n, total_def, total_good = len(df), int(y.sum()), int(len(y) - y.sum())
    grid = np.round(np.arange(0.0, 1.0001, 0.01), 2)

    k, good, defaults, ev = curve(y, RATIOS)
    idx = np.round(grid * n).astype(int)
    cur = pd.DataFrame({"approval_rate": grid, "approved": idx,
                        "bad_rate_among_approved": np.where(idx > 0, defaults[idx] / np.maximum(idx, 1), np.nan),
                        "share_of_defaults_declined": 1 - defaults[idx] / total_def,
                        "share_of_good_declined": 1 - good[idx] / total_good})
    for X in RATIOS:
        cur[f"ev_per_1000_X{X}"] = ev[X][idx] / n * 1000
    cur.round(4).to_csv(OUT_DIR / "cutoff_curve.csv", index=False)

    rng = np.random.default_rng(SEED)
    rows = []
    for X in RATIOS:
        best = grid[np.argmax(ev[X][idx])]
        i = int(round(best * n))
        ev_max = ev[X][idx].max()
        boots = []
        for _ in range(N_BOOT):
            s = rng.integers(0, n, n)
            order = np.argsort(df[SCORE].to_numpy()[s], kind="mergesort")
            boots.append(best_rate(y[s][order], X, grid))
        p_star = 1 / (1 + X)
        k_theory = int((df[SCORE] < p_star).sum())
        theory = k_theory / n
        ev_theory = ev[X][k_theory]
        rows.append({"X (loss per default / profit per good)": X,
                     "break_even_default_prob": round(p_star, 3),
                     "theory_approval_rate": round(theory, 3),
                     "simulated_best_approval_rate": best,
                     "bootstrap_5th_to_95th": f"{np.percentile(boots, 5):.0%} to {np.percentile(boots, 95):.0%}",
                     "bad_rate_among_approved": round(defaults[i] / max(i, 1), 4),
                     "share_of_defaults_declined": round(1 - defaults[i] / total_def, 3),
                     "share_of_good_declined": round(1 - good[i] / total_good, 3),
                     "ev_per_1000_at_best": round(ev_max / n * 1000, 1),
                     "ev_per_1000_at_theory_cutoff": round(ev_theory / n * 1000, 1),
                     "theory_cutoff_as_pct_of_best_ev": round(ev_theory / ev_max, 3)})
    scen = pd.DataFrame(rows)
    scen.to_csv(OUT_DIR / "scenario_table.csv", index=False)

    # Robust three-tier rule from the extreme cost ratios
    lo, hi = 1 / (1 + max(RATIOS)), 1 / (1 + min(RATIOS))
    tiers = pd.cut(df[SCORE], [-1, lo, hi, 2], labels=[
        f"A: eligible in every scenario (p < {lo:.1%})",
        f"B: depends on the cost ratio ({lo:.1%} to {hi:.1%})",
        f"C: not eligible in any scenario (p >= {hi:.1%})"])
    tt = df.groupby(tiers, observed=True).agg(accounts=("default", "size"),
                                              actual_default_rate=("default", "mean"),
                                              avg_predicted=(SCORE, "mean")).reset_index()
    tt = tt.rename(columns={tt.columns[0]: "tier"})
    tt["share_of_accounts"] = tt["accounts"] / n
    tt["share_of_all_defaults"] = df.groupby(tiers, observed=True)["default"].sum().to_numpy() / total_def
    tt.round(4).to_csv(OUT_DIR / "tiers.csv", index=False)

    # Screening check on groups NOT used by the model, at the central-case cutoff
    p_star = 1 / (1 + CENTRAL_X)
    df["eligible"] = df[SCORE] < p_star
    df["age_band"] = pd.cut(df["AGE"], [0, 29, 39, 49, 120], labels=["<30", "30-39", "40-49", "50+"])
    fair = []
    for col, label in [("SEX", "sex (1=male, 2=female)"), ("age_band", "age band")]:
        g = df.groupby(col, observed=True).agg(accounts=("eligible", "size"), eligible_rate=("eligible", "mean"),
                                               actual_default_rate=("default", "mean")).reset_index()
        g.insert(0, "group_type", label)
        g = g.rename(columns={col: "group"})
        g["eligible_rate_vs_highest"] = g["eligible_rate"] / g["eligible_rate"].max()
        fair.append(g)
    fair = pd.concat(fair).round(4)
    fair.to_csv(OUT_DIR / "group_screening.csv", index=False)

    lines = ["# Strategy Simulation Summary", "",
             f"Hold-out accounts: {n:,}; default rate {y.mean():.2%}; score used: gradient boosting probability.",
             "Framing: an eligible good account earns 1 unit; an eligible account that defaults costs X units.", "",
             "## Best cutoff by cost ratio", "", scen.to_markdown(index=False), "",
             "## Three-tier rule that holds across X = 3 to 12", "", tt.round(4).to_markdown(index=False), "",
             f"## Screening check at the central case (X = {CENTRAL_X}, cutoff {p_star:.1%})", "",
             fair.to_markdown(index=False)]
    SUMMARY.write_text("\n".join(lines))
    print(scen.T.to_string(header=False)); print(); print(tt.round(4).to_string(index=False)); print(); print(fair.to_string(index=False))


if __name__ == "__main__":
    main()
