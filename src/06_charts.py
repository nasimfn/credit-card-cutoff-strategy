"""
Step 6: Charts for the credit strategy report. Each chart states its source and key caveat.

Input : data/processed/scored_test.csv, reports/strategy/*.csv
Output: reports/figures/*.png
"""
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path("reports/figures")
SOURCE = ("Data: Default of Credit Card Clients (Yeh & Lien, 2009; UCI), 30,000 Taiwanese cardholders, "
          "Apr-Sep 2005. Results are on a 9,000-account hold-out set. The profit framing is illustrative "
          "and is not based on any lender's data.")
COL = {"logistic": "#8d99ae", "gbm": "#1b6ca8", "A": "#2a9d8f", "B": "#e9c46a", "C": "#d1495b"}
XS = {3: "#2a9d8f", 5: "#1b6ca8", 8: "#e9a03b", 12: "#d1495b"}


def footer(fig, extra=""):
    text = "\n".join(textwrap.fill(t, 135) for t in ([extra] if extra else []) + [SOURCE])
    fig.text(0.01, 0.01, text, fontsize=7, color="#555", va="bottom")


def clean_axes(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", alpha=0.3)


def calibration_bands(y, p, bins=10):
    d = pd.DataFrame({"y": y, "p": p})
    d["b"] = pd.qcut(d["p"].rank(method="first"), bins, labels=False)
    g = d.groupby("b").agg(pred=("p", "mean"), actual=("y", "mean"))
    return g


def chart_calibration(sc):
    fig, ax = plt.subplots(figsize=(7.5, 6))
    for name, col, label in [("gbm", "p_gbm", "Gradient boosting"), ("logistic", "p_logistic", "Logistic regression")]:
        g = calibration_bands(sc["default"], sc[col])
        ax.plot(g["pred"], g["actual"], marker="o", color=COL[name], lw=2, label=label)
    ax.plot([0, 0.8], [0, 0.8], ls="--", color="#999", label="Perfect calibration")
    ax.set_title("Predicted vs actual default rate, by risk band", loc="left", fontweight="bold")
    ax.set_xlabel("Average predicted default probability")
    ax.set_ylabel("Actual default rate")
    ax.legend(frameon=False); clean_axes(ax)
    fig.subplots_adjust(bottom=0.24)
    footer(fig, "Each dot is one tenth of the accounts (900). Dots near the dashed line mean the scores can be read as probabilities.")
    fig.savefig(OUT / "01_calibration.png", dpi=150); plt.close(fig)


def chart_value(curve, scen):
    fig, ax = plt.subplots(figsize=(10, 5.4))
    for X in (3, 5, 8, 12):
        ax.plot(curve["approval_rate"] * 100, curve[f"ev_per_1000_X{X}"], color=XS[X], lw=1.8,
                label=f"Each default costs {X}x the profit of a good account")
        r = scen.loc[scen.iloc[:, 0] == X].iloc[0]
        k = curve.iloc[(curve["approval_rate"] - r["theory_approval_rate"]).abs().argmin()]
        ax.scatter([k["approval_rate"] * 100], [k[f"ev_per_1000_X{X}"]], color=XS[X], s=55, zorder=3, edgecolor="white")
    ax.set_title("Value per 1,000 accounts by eligibility cutoff", loc="left", fontweight="bold")
    ax.set_xlabel("Share of accounts made eligible (lowest risk first)")
    ax.set_ylabel("Value per 1,000 accounts (units of profit)")
    ax.set_ylim(-150, 520); ax.set_xlim(0, 100)
    ax.axhline(0, color="#999", lw=0.8)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left"); clean_axes(ax)
    fig.subplots_adjust(bottom=0.25)
    footer(fig, "The vertical axis is cut off at -150; curves keep falling beyond it. "
                "Dots mark the simple break-even rule (eligible while predicted default probability < 1/(1+X)). "
                "The curves are flat near their peaks, so the exact best cutoff is uncertain.")
    fig.savefig(OUT / "02_value_by_cutoff.png", dpi=150); plt.close(fig)


def chart_tradeoff(curve, tiers, portfolio_rate):
    fig, ax = plt.subplots(figsize=(10, 5.4))
    a, b = tiers["share_of_accounts"].iloc[0] * 100, tiers["share_of_accounts"].iloc[:2].sum() * 100
    ax.axvspan(0, a, color=COL["A"], alpha=0.15); ax.axvspan(a, b, color=COL["B"], alpha=0.18)
    ax.axvspan(b, 100, color=COL["C"], alpha=0.15)
    ax.plot(curve["approval_rate"] * 100, curve["bad_rate_among_approved"] * 100, color="#1b6ca8", lw=2.2)
    ax.set_ylim(2, 28)
    ax.axhline(portfolio_rate * 100, ls=":", color="#555")
    ax.text(99, portfolio_rate * 100 + 0.5, f"Portfolio average {portfolio_rate:.1%}", fontsize=8, color="#555", ha="right")
    ymax = ax.get_ylim()[1]
    for x, t in [(a / 2, "A: eligible in\nevery scenario"), ((a + b) / 2, "B: depends on\nthe cost ratio"),
                 ((b + 100) / 2, "C: not eligible\nin any scenario")]:
        ax.text(x, ymax * 0.93, t, ha="center", va="top", fontsize=9, fontweight="bold")
    ax.set_title("Default rate among eligible accounts as the cutoff widens", loc="left", fontweight="bold")
    ax.set_xlabel("Share of accounts made eligible (lowest risk first)")
    ax.set_ylabel("Default rate among eligible accounts (%)")
    ax.set_xlim(0, 100); clean_axes(ax)
    fig.subplots_adjust(bottom=0.25)
    footer(fig, "Tier edges come from the break-even rule at the extreme cost ratios (3x and 12x).")
    fig.savefig(OUT / "03_tradeoff_and_tiers.png", dpi=150); plt.close(fig)


def chart_tiers(tiers):
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    labels = ["A: eligible in\nevery scenario", "B: depends on\nthe cost ratio", "C: not eligible\nin any scenario"]
    x = np.arange(3); w = 0.36
    b1 = ax.bar(x - w / 2, tiers["share_of_accounts"] * 100, w, color="#8d99ae", label="Share of accounts")
    b2 = ax.bar(x + w / 2, tiers["share_of_all_defaults"] * 100, w, color="#d1495b", label="Share of all defaults")
    for bars in (b1, b2):
        for r in bars:
            ax.text(r.get_x() + r.get_width() / 2, r.get_height() + 1, f"{r.get_height():.0f}%", ha="center", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("Percent"); ax.set_ylim(0, 70)
    c = tiers.iloc[2]
    ax.set_title(f"Tier C is {c['share_of_accounts']:.0%} of accounts but {c['share_of_all_defaults']:.0%} of defaults",
                 loc="left", fontweight="bold")
    ax.legend(frameon=False); clean_axes(ax)
    fig.subplots_adjust(bottom=0.25)
    r = tiers["actual_default_rate"]
    footer(fig, f"Default rates within tiers: A {r.iloc[0]:.1%}, B {r.iloc[1]:.1%}, C {r.iloc[2]:.1%}.")
    fig.savefig(OUT / "04_tier_concentration.png", dpi=150); plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    sc = pd.read_csv("data/processed/scored_test.csv")
    curve = pd.read_csv("reports/strategy/cutoff_curve.csv")
    scen = pd.read_csv("reports/strategy/scenario_table.csv")
    tiers = pd.read_csv("reports/strategy/tiers.csv")
    chart_calibration(sc); chart_value(curve, scen); chart_tradeoff(curve, tiers, sc["default"].mean()); chart_tiers(tiers)
    print("Saved:", *sorted(p.name for p in OUT.glob("*.png")), sep="\n  ")
