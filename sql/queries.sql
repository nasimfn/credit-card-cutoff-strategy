-- Credit card portfolio queries (SQLite)
-- Note: 'default' is a reserved word in SQL, so the outcome column is named 'defaulted' in these tables.
-- Tables: scored   (9,000 hold-out accounts with model scores; p_gbm = predicted default probability)
--         accounts (all 30,000 accounts, cleaned, with behavioural features)

-- name: risk_band_summary
-- Ten equal-sized risk bands from the gradient boosting score (1 = lowest risk).
SELECT risk_band,
       COUNT(*)                              AS accounts,
       ROUND(MIN(p_gbm), 3)                  AS min_score,
       ROUND(MAX(p_gbm), 3)                  AS max_score,
       ROUND(AVG(p_gbm), 4)                  AS avg_predicted_default,
       ROUND(AVG(defaulted), 4)                AS actual_default_rate,
       ROUND(AVG(LIMIT_BAL), 0)              AS avg_credit_limit
FROM (SELECT *, NTILE(10) OVER (ORDER BY p_gbm) AS risk_band FROM scored)
GROUP BY risk_band
ORDER BY risk_band;

-- name: cutoff_table_5pct_steps
-- If we make the lowest-risk X% of accounts eligible, what is the default rate among them?
-- A recursive CTE generates the 5% steps; a running total over the risk ordering gives the cumulative counts.
WITH RECURSIVE steps(s) AS (SELECT 1 UNION ALL SELECT s + 1 FROM steps WHERE s < 20),
ranked AS (
    SELECT defaulted,
           ROW_NUMBER() OVER (ORDER BY p_gbm, ID)                              AS rn,
           SUM(defaulted) OVER (ORDER BY p_gbm, ID ROWS UNBOUNDED PRECEDING)     AS cum_defaults,
           COUNT(*) OVER ()                                                    AS total,
           SUM(defaulted) OVER ()                                                AS total_defaults
    FROM scored
)
SELECT s * 5 || '%'                                         AS approval_rate,
       r.rn                                                 AS accounts_eligible,
       ROUND(1.0 * r.cum_defaults / r.rn, 4)                AS default_rate_among_eligible,
       ROUND(1.0 - 1.0 * r.cum_defaults / r.total_defaults, 3) AS share_of_all_defaults_declined
FROM steps
JOIN ranked r ON r.rn = CAST(r.total * s / 20.0 AS INTEGER)
ORDER BY s;

-- name: tier_summary
-- Three-tier rule that holds for every cost ratio from X = 3 to X = 12:
-- below 1/13 (7.7%) eligible in every scenario; at or above 1/4 (25%) eligible in none.
SELECT tier,
       COUNT(*)                                               AS accounts,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)     AS pct_of_accounts,
       ROUND(AVG(defaulted), 4)                                 AS actual_default_rate,
       ROUND(100.0 * SUM(defaulted) / SUM(SUM(defaulted)) OVER (), 1) AS pct_of_all_defaults
FROM (SELECT defaulted,
             CASE WHEN p_gbm < 1.0 / 13 THEN 'A: eligible in every scenario'
                  WHEN p_gbm < 1.0 / 4  THEN 'B: depends on cost ratio'
                  ELSE 'C: not eligible in any scenario' END AS tier
      FROM scored)
GROUP BY tier
ORDER BY tier;

-- name: delinquency_and_utilisation_segments
-- Full 30,000 accounts: default rate by worst delay in the last 6 months and latest card utilisation.
SELECT CASE WHEN max_delay = 0 THEN '0: never late'
            WHEN max_delay = 1 THEN '1: one month late'
            WHEN max_delay = 2 THEN '2: two months late'
            ELSE '3+: three or more months late' END           AS worst_delay,
       CASE WHEN util_latest < 0.3 THEN 'under 30%'
            WHEN util_latest < 0.7 THEN '30% to 70%'
            ELSE '70% or more' END                             AS latest_utilisation,
       COUNT(*)                                                AS accounts,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)      AS pct_of_accounts,
       ROUND(AVG(defaulted), 4)                                  AS default_rate
FROM accounts
GROUP BY 1, 2
ORDER BY 1, MIN(util_latest);
