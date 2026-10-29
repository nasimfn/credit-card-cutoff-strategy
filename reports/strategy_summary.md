# Strategy Simulation Summary

Hold-out accounts: 9,000; default rate 22.12%; score used: gradient boosting probability.
Framing: an eligible good account earns 1 unit; an eligible account that defaults costs X units.

## Best cutoff by cost ratio

|   X (loss per default / profit per good) |   break_even_default_prob |   theory_approval_rate |   simulated_best_approval_rate | bootstrap_5th_to_95th   |   bad_rate_among_approved |   share_of_defaults_declined |   share_of_good_declined |   ev_per_1000_at_best |   ev_per_1000_at_theory_cutoff |   theory_cutoff_as_pct_of_best_ev |
|-----------------------------------------:|--------------------------:|-----------------------:|-------------------------------:|:------------------------|--------------------------:|-----------------------------:|-------------------------:|----------------------:|-------------------------------:|----------------------------------:|
|                                        3 |                     0.25  |                  0.739 |                           0.76 | 71% to 78%              |                    0.1275 |                        0.562 |                    0.149 |                 372.4 |                          368.4 |                             0.989 |
|                                        5 |                     0.167 |                  0.574 |                           0.46 | 41% to 58%              |                    0.0877 |                        0.818 |                    0.461 |                 218   |                          209.8 |                             0.962 |
|                                        8 |                     0.111 |                  0.329 |                           0.32 | 25% to 40%              |                    0.066  |                        0.905 |                    0.616 |                 130   |                          126.4 |                             0.973 |
|                                       12 |                     0.077 |                  0.186 |                           0.2  | 15% to 25%              |                    0.0489 |                        0.956 |                    0.756 |                  72.9 |                           69.2 |                             0.95  |

## Three-tier rule that holds across X = 3 to 12

| tier                                         |   accounts |   actual_default_rate |   avg_predicted |   share_of_accounts |   share_of_all_defaults |
|:---------------------------------------------|-----------:|----------------------:|----------------:|--------------------:|------------------------:|
| A: eligible in every scenario (p < 7.7%)     |       1676 |                0.0483 |          0.0599 |              0.1862 |                  0.0407 |
| B: depends on the cost ratio (7.7% to 25.0%) |       4976 |                0.1513 |          0.1447 |              0.5529 |                  0.3782 |
| C: not eligible in any scenario (p >= 25.0%) |       2348 |                0.4928 |          0.4924 |              0.2609 |                  0.5811 |

## Screening check at the central case (X = 5, cutoff 16.7%)

| group_type             | group   |   accounts |   eligible_rate |   actual_default_rate |   eligible_rate_vs_highest |
|:-----------------------|:--------|-----------:|----------------:|----------------------:|---------------------------:|
| sex (1=male, 2=female) | 1       |       3563 |          0.5568 |                0.2386 |                     0.9503 |
| sex (1=male, 2=female) | 2       |       5437 |          0.586  |                0.2099 |                     1      |
| age band               | <30     |       2882 |          0.5347 |                0.2245 |                     0.8798 |
| age band               | 30-39   |       3332 |          0.6077 |                0.1984 |                     1      |
| age band               | 40-49   |       1958 |          0.5878 |                0.239  |                     0.9673 |
| age band               | 50+     |        828 |          0.5471 |                0.2597 |                     0.9002 |