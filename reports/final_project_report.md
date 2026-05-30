# QQQ Signal Research Report

I built this project to study a narrow but practical question: can a small set
of interpretable QQQ timing rules improve the risk profile of holding Nasdaq
exposure, or do they disappear once the backtest is run with proper timing,
costs, and a real validation split?

The repository contains the runnable version of that workflow. It does
not ship the original private challenge dataset, so the committed output files
are generated from a sanitized included sample covering `2018-01-02` through
`2025-06-30`. That included sample is long enough to show how the pipeline works,
how the signal sleeves interact, and how the validation logic behaves, even
though it is not a full reproduction of the private-run finalist result.

The core design of the project is simple. Each sleeve maps daily market
information into a target QQQ exposure between `-1.0` and `1.5`. The data is
minimal by design: QQQ close/high/low plus DXY. From that input, the code
builds trend, volatility, oversold, macro, and seasonality signals rather than
fitting a large black-box feature model.

The signal set includes:

- long-term trend
- medium-term trend
- volatility / oversold mean reversion
- defensive volatility overlays
- shock and skew risk controls
- cross-asset confirmation through DXY
- month-turn seasonality

Every sleeve produces a daily target exposure. That exposure is applied to the
next day's QQQ return, not the same day's return. This shifted-exposure rule is
one of the most important integrity choices in the repo because it keeps the
signal path from accidentally using same-day information twice. Turnover is
tracked directly, and one-way transaction costs are charged against exposure
changes.

The original project was designed around a long train / validation /
blind-holdout split:

| Split | Dates | Purpose |
|---|---:|---|
| Train | 2000-01-01 to 2015-12-31 | Develop and discard hypotheses |
| Validation | 2016-01-01 to 2021-12-31 | Choose sleeves and form the ensemble |
| Blind holdout | 2022-01-01 to 2025-06-30 | Final out-of-sample evaluation |

Because the committed included sample is shorter, the repo uses:

| Public split | Dates | Purpose |
|---|---:|---|
| Train | 2018-01-01 to 2020-12-31 | First-pass signal work |
| Validation | 2021-01-01 to 2022-12-31 | Sleeve selection on the included sample |
| Holdout | 2023-01-01 to 2025-06-30 | Final public-sample evaluation |

The selection step is validation-only. Signals are first grouped by family and
ranked using validation Sharpe, validation drawdown, turnover, and cost drag.
Near-duplicate validation profiles are then removed so the final ensemble does
not quietly become several versions of the same exposure path. On the committed
included sample, the final ensemble consists of:

- `medium_term_trend`
- `rsi_deep_value`
- `turn_of_month`

That selection logic matters because it is where many timing projects cheat.
This repo keeps the holdout period for reporting, not for iterative membership
changes.

The public-sample results are intentionally mixed. The final public ensemble
improves holdout drawdown relative to buy-and-hold, but its holdout Sharpe is
still negative. That is not the most flattering output, but it is the right one
to leave in the repo. The point of the project is not to prove that every
included sample says the strategy is great. The point is to show the full process:
how sleeves are built, how they are selected, how costs matter, and what
happens when a sanitized sample does not reproduce the private-run headline.

At the same time, the repo does document the original challenge result
separately. The preserved summary states that the original finalist submission
reported net blind-holdout Sharpe above `1.3` after costs over
`2022-01-01` to `2025-06-30`. That result is summarized in
[reports/original_challenge_summary.md](original_challenge_summary.md) and the
supporting CSV summaries in `results/`, but it is not falsely presented as a
publicly reproduced backtest from the sanitized sample.

So the cleanest way to read the project is:

- the repo proves the workflow, code path, and research discipline
- the included sample gives an honest, runnable signal-comparison benchmark
- the original challenge summary records the stronger private-run result that
 motivated the project in the first place

The committed deliverables are therefore not just code. They are the code plus
the decisions around it:

- signal implementations in `src/`
- a cost-aware no-lookahead backtest
- selection and ensemble logic
- CSV summaries for performance, cost sensitivity, parameter sensitivity, and
 regimes
- figure outputs for equity, drawdown, rolling Sharpe, and correlation
- a project notebook and supporting notes

That combination is what I wanted the repository to show: not “here is one
backtest number,” but “here is the full research loop I used to build, test,
select, and document the strategy.”
