# QQQ Signal Research Report

This project studies a simple question: can a small set of clear QQQ timing
rules improve on buy-and-hold once the backtest is run carefully?

The repo is the runnable version of that work. The original finalist submission
used challenge-provided QQQ data that I cannot post here, so the repo uses a
smaller included dataset with the same kind of inputs. That dataset is enough
to run the whole pipeline and show how the project works.

The setup is straightforward. Each signal maps daily market information into a
target QQQ exposure between `-1.0` and `1.5`. The signals are built from QQQ
price behavior, range-based volatility, and DXY. The goal was to keep the
rules interpretable rather than hide everything inside a large model.

The signals cover a few main ideas:

- trend
- oversold mean reversion
- defensive volatility control
- cross-asset confirmation
- seasonality

The backtest applies today's chosen exposure to tomorrow's return and charges
transaction costs when exposure changes. That one-day shift is a key part of
the design because it avoids a common look-ahead mistake.

The original submission used a long train / validation / blind-holdout split:

| Split | Dates | Purpose |
|---|---:|---|
| Train | 2000-01-01 to 2015-12-31 | develop and discard ideas |
| Validation | 2016-01-01 to 2021-12-31 | choose signals and build the ensemble |
| Blind holdout | 2022-01-01 to 2025-06-30 | final evaluation |

The included dataset is shorter, so the repo uses:

| Split | Dates | Purpose |
|---|---:|---|
| Train | 2018-01-01 to 2020-12-31 | first-pass work |
| Validation | 2021-01-01 to 2022-12-31 | choose signals on the included dataset |
| Holdout | 2023-01-01 to 2025-06-30 | final out-of-sample check |

The final ensemble on the included dataset is:

- `medium_term_trend`
- `rsi_deep_value`
- `turn_of_month`

That selection is validation-only. The holdout period is reported after the
membership is fixed.

The included-dataset results are mixed. The final ensemble improves drawdown
relative to buy-and-hold, but its holdout Sharpe is still negative. I left that
result in the repo because it is more informative than pretending the included
dataset reproduced the stronger original submission.

So the clean way to read the project is:

- the repo shows the full research process
- the included dataset gives a runnable version of the workflow
- the original challenge summary records the stronger finalist result

That original result is documented separately in
[original_challenge_summary.md](original_challenge_summary.md).
