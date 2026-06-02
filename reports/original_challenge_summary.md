# Original Quanta Challenge Summary

This note is the short record of the original QQQ project from the Quanta QR
Fellowship finalist process.

The original submission used a longer QQQ dataset provided through the
challenge. I cannot redistribute that dataset here, so the GitHub repo uses a
smaller included dataset for the runnable version of the project.

The original workflow used:

| Split | Dates | Purpose |
|---|---:|---|
| Train | 2000-01-01 to 2015-12-31 | develop signal ideas |
| Validation | 2016-01-01 to 2021-12-31 | choose signals and build the ensemble |
| Blind holdout | 2022-01-01 to 2025-06-30 | final evaluation |

The saved project materials say the final ensemble achieved net blind-holdout
Sharpe above `1.3` after costs over `2022-01-01` to `2025-06-30`.

I do not have a full raw output table from that submission in the repo, so this
should be read as a saved project summary, not as a full recreation from the
original inputs.

What the repo adds is the full code path:

- signal definitions
- no-lookahead backtesting
- transaction-cost modeling
- validation-based selection
- sensitivity and regime checks

So the repo and this note do different jobs. The repo shows how I did the work.
This note keeps the headline result from the original submission.

Supporting files:

- [original_challenge_evidence/README.md](original_challenge_evidence/README.md)
- [../results/original_challenge_performance_summary.csv](../results/original_challenge_performance_summary.csv)
