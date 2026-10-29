"""
Step 8: Build the PDF project summary to attach to a job application.

Set GITHUB_URL once the repository is published, then rerun this script.
Output: docs/Project_Summary_Credit_Strategy_Nasim_Feizinazhad.pdf
"""
import json
from pathlib import Path

import pandas as pd
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

GITHUB_URL = "https://github.com/nasimfn/credit-card-cutoff-strategy"

OUT = Path("docs/Project_Summary_Credit_Strategy_Nasim_Feizinazhad.pdf")
FIG = Path("reports/figures")
NAVY, GREY, LIGHT = colors.HexColor("#1f3a5f"), colors.HexColor("#555555"), colors.HexColor("#eef2f7")

base = getSampleStyleSheet()
body = ParagraphStyle("body", parent=base["Normal"], fontName="Helvetica", fontSize=9.2, leading=12.2,
                      alignment=TA_LEFT, spaceAfter=3)
small = ParagraphStyle("small", parent=body, fontSize=8, leading=10.4, textColor=GREY)
cell = ParagraphStyle("cell", parent=body, fontSize=8.4, leading=10.6, spaceAfter=0)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")
h1 = ParagraphStyle("h1", parent=base["Title"], fontName="Helvetica-Bold", fontSize=15.5, leading=19,
                    textColor=NAVY, alignment=TA_LEFT, spaceAfter=2)
h2 = ParagraphStyle("h2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=10.5, leading=13,
                    textColor=NAVY, spaceBefore=7, spaceAfter=3, keepWithNext=1)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=11, bulletIndent=1, spaceAfter=2)


def bullets(items):
    return [Paragraph(t, bullet, bulletText="-") for t in items]


def table(rows, widths):
    data = [[Paragraph(c, cellb if i == 0 else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * inch for w in widths], repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), LIGHT),
                           ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9d1dc")),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]))
    return t


def fit_image(path, width):
    w, h = PILImage.open(path).size
    return Image(str(path), width=width, height=width * h / w)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GREY)
    canvas.drawString(0.8 * inch, 0.5 * inch, "Nasim Feizinazhad | Project summary: credit card eligibility cutoff strategy")
    canvas.drawRightString(letter[0] - 0.8 * inch, 0.5 * inch, f"Page {doc.page}")
    canvas.restoreState()


def main():
    m = json.loads(Path("reports/model_metrics.json").read_text())["results"]
    tiers = pd.read_csv("reports/strategy/tiers.csv")
    scen = pd.read_csv("reports/strategy/scenario_table.csv")
    A, B, C = (tiers.iloc[i] for i in range(3))
    capture = scen["theory_cutoff_as_pct_of_best_ev"]
    OUT.parent.mkdir(exist_ok=True)
    doc = SimpleDocTemplate(str(OUT), pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                            topMargin=0.65 * inch, bottomMargin=0.8 * inch,
                            title="Credit Card Eligibility Cutoff Strategy", author="Nasim Feizinazhad")
    s = []
    s.append(Paragraph("Credit Card Eligibility Cutoff Strategy:<br/>From Default Risk to a Decision", h1))
    s.append(Paragraph("Personal portfolio project built on public data. It is not work experience and does not "
                       "use any lender's data. All profit and cost figures are illustrative assumptions.", small))
    s.append(Paragraph(f'Code and documentation: <link href="{GITHUB_URL}" color="#1f3a5f">{GITHUB_URL}</link>', small))

    s.append(Paragraph("The question and the answer", h2))
    s.append(Paragraph(
        "Where should a lender set a risk cutoff, what does each choice cost, and what would change the answer? "
        "The data is existing cardholders, so I framed the decision as eligibility for a credit limit increase: an "
        "eligible account that stays good earns 1 unit, and one that defaults costs X units. X is unknown, so every "
        "result is shown for X = 3, 5, 8 and 12.", body))
    s.append(table([
        ("Tier", "Predicted default probability", "Share of accounts", "Actual default rate", "Share of all defaults", "Decision"),
        ("A", "below 7.7%", f"{A.share_of_accounts:.1%}", f"{A.actual_default_rate:.1%}", f"{A.share_of_all_defaults:.1%}",
         "Eligible under every cost ratio tested"),
        ("B", "7.7% to 25%", f"{B.share_of_accounts:.1%}", f"{B.actual_default_rate:.1%}", f"{B.share_of_all_defaults:.1%}",
         "Depends on the cost ratio: a business judgment"),
        ("C", "25% or more", f"{C.share_of_accounts:.1%}", f"{C.actual_default_rate:.1%}", f"{C.share_of_all_defaults:.1%}",
         "Not eligible under any cost ratio tested"),
    ], [0.4, 1.35, 0.9, 0.95, 1.0, 2.25]))
    s.append(Spacer(1, 4))
    s.append(Paragraph(
        f"For tier B, a simple break-even rule applies: make an account eligible while its predicted default "
        f"probability is below 1/(1+X). It captured {capture.min():.0%} to {capture.max():.0%} of the best value found "
        f"by simulation in all four scenarios. The single best cutoff is uncertain, because the value curves are flat near "
        f"their peaks. What would change the answer: real revenue and loss figures, evidence of how limit increases "
        f"change behaviour, and a population different from this 2005 Taiwanese sample.", body))

    s.append(Paragraph("How the project works, step by step", h2))
    s.append(table([
        ("#", "Step", "What it does", "Result"),
        ("1", "Download", "Gets the public UCI Default of Credit Card Clients dataset (30,000 clients, Taiwan, 2005).", "30,000 rows"),
        ("2", "Validate", "Runs 22 data quality checks on the raw data and logs every failing record.", "14 checks with findings"),
        ("3", "Clean", "Applies documented decisions (undocumented codes, duplicates) and builds six features from account "
                       "behaviour only. Sex, education, marital status and age are excluded from the model.", "32-column clean file"),
        ("4", "Model", "Trains logistic regression and gradient boosting, and compares them with one-variable baselines.",
         f"AUC {m['logistic']['auc']:.3f} and {m['gradient_boosting']['auc']:.3f} vs {m['baseline_latest_repayment_status']['auc']:.3f}"),
        ("5", "Simulate strategy", "Tests cutoffs under four cost ratios, checks the break-even rule, and bootstraps the "
                                   "uncertainty. Screens the cutoff for gaps by sex and age.", "Three-tier rule"),
        ("6", "Query in SQL", "Loads the scored accounts into SQLite and runs four queries: risk bands, cutoff table, tiers, "
                              "segments.", "4 result tables"),
        ("7", "Chart", "Draws four charts, each stating its source and key caveat.", "4 figures"),
        ("8", "Document and verify", "Writes a data dictionary (32 and 13 fields) and a README, then reruns every script "
                                     "from a fresh clone of the repository.", "Outputs identical"),
    ], [0.25, 1.1, 3.85, 1.65]))

    s.append(Paragraph("What the data and models showed", h2))
    s += bullets([
        "<b>Data quality.</b> No missing values or duplicate IDs, but 345 education codes and 54 marital-status codes "
        "that the source does not define, and repayment codes (-2 and 0) that it does not define for most accounts. "
        "A one-month delay is common in September (3,688 accounts) but almost absent in earlier months. Accounts coded "
        "'paid duly' default more (16.8%) than accounts coded 0 (12.8%). These were flagged, not corrected.",
        f"<b>Models are good, not magic.</b> On 9,000 hold-out accounts, gradient boosting scored AUC "
        f"{m['gradient_boosting']['auc']:.3f} (cross-validation {m['gradient_boosting']['cv_auc_mean']:.3f}) and logistic "
        f"regression {m['logistic']['auc']:.3f}, against {m['baseline_latest_repayment_status']['auc']:.3f} for a single "
        f"repayment-status rule. Predicted and actual default rates agree to within about 3.5 percentage points in every risk band.",
        f"<b>Concentration of risk.</b> Tier C is {C.share_of_accounts:.0%} of accounts but {C.share_of_all_defaults:.0%} of "
        f"defaults; tier A is {A.share_of_accounts:.0%} of accounts and {A.share_of_all_defaults:.0%} of defaults.",
        "<b>Screening check.</b> At the central cutoff, the share made eligible is 55.7% for men and 58.6% for women, and "
        "between 53.5% and 60.8% across age bands (lowest to highest ratio 0.88). Default rates also differ by group, so "
        "this is a screening check, not a fairness or legal test.",
    ])

    s.append(KeepTogether([Paragraph("Chart: risk is concentrated in tier C", h2),
                           fit_image(FIG / "04_tier_concentration.png", 4.2 * inch)]))
    s.append(KeepTogether([Paragraph("Chart: value by cutoff under four cost ratios", h2),
                           fit_image(FIG / "02_value_by_cutoff.png", 4.9 * inch)]))

    s.append(Paragraph("Limitations", h2))
    s += bullets([
        "The data is from Taiwan in 2005, not Canadian cards. The cost ratio and the limit-increase framing are "
        "assumptions, not findings.",
        "About 1,991 hold-out defaults make cutoff estimates noisy; the bootstrap range for the best approval rate is "
        "wide (41% to 58% at X = 5).",
        "Excluding sex, education, marital status and age does not guarantee no indirect effect. This is not a "
        "regulatory-grade validation, and there is no time dimension to test stability.",
        "Source: Yeh, I. (2009). Default of Credit Card Clients. UCI Machine Learning Repository, "
        "doi.org/10.24432/C55S3H (CC BY 4.0). A CSV copy of the data was used, not the UCI file itself.",
    ])
    s.append(Spacer(1, 4))
    s.append(Paragraph("<b>Tools:</b> Python (pandas, scikit-learn, matplotlib), SQL (SQLite), Git. Developed with assistance "
                       "from Claude (Anthropic) for drafting and reviewing code; the analytical decisions above were "
                       "reviewed and chosen by me.", small))
    doc.build(s, onFirstPage=footer, onLaterPages=footer)
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
