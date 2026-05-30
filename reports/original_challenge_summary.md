# Original Quanta Challenge Results

## Purpose

This report summarizes the original QQQ signal-research project completed for the Quanta QR Fellowship finalist challenge.

This repository contains the runnable version of the research framework. The
included dataset still shows the mechanics of the pipeline: signal
construction, no-lookahead backtesting, transaction-cost modeling, sensitivity
analysis, and regime evaluation.

The original challenge used a longer QQQ dataset provided through the Quanta QR
Fellowship challenge. That source data is not redistributed here, but the
research protocol and final result summaries are documented below.

I assembled this GitHub repo later from my private research archive, which is
why some summary files and evidence notes have newer commit dates than the
original submission period.

## Original Research Protocol

The original project used the following split:

| Split | Dates | Purpose |
|---|---:|---|
| Train | 2000-01-01 to 2015-12-31 | Signal hypothesis development |
| Validation | 2016-01-01 to 2021-12-31 | Signal selection and ensemble construction |
| Blind holdout | 2022-01-01 to 2025-06-30 | Final out-of-sample evaluation |

The blind holdout period was not used for signal development.

## Backtest Assumptions

- Daily QQQ exposure strategy.
- Exposure constrained to `[-1.0, 1.5]`.
- Exposure chosen using information available at or before the trade date.
- Position held until the next close.
- Transaction costs included in final reported results.
- Final signals were evaluated using train / validation / blind-holdout separation.
- Robustness checks included +/- 10% parameter sensitivity and regime-sliced analysis.

## Signal Families

The final research process evaluated signals across the following families:

- Trend-following
- Mean reversion
- Volatility regime
- Cross-asset macro
- Volume / liquidity
- Seasonality
- Short-bias / defensive overlays

## Final Original-Challenge Results

The preserved challenge materials report that the final ensemble achieved net blind-holdout Sharpe above 1.3 after transaction costs over 2022-01-01 to 2025-06-30.

Exact full metric tables from the challenge run are not redistributed here
because the source dataset is not mine to post and the preserved materials
retained the headline result rather than the complete raw output. This
repository therefore documents the original result as a summary statistic, not
as a recreated raw backtest table.

| Strategy | Validation Sharpe | Blind-Holdout Sharpe | Max Drawdown | Notes |
|---|---:|---:|---:|---|
| Buy-and-hold QQQ | NA | NA | NA | Benchmark on the original private dataset |
| Best single signal | NA | NA | NA | Strongest standalone signal on the original private dataset |
| Final ensemble | NA | >1.3 | NA | Final selected portfolio; the preserved project materials retained the headline after-cost Sharpe rather than the full raw metric table |

## Robustness Checks

The original analysis included:

- ±10% parameter sensitivity checks.
- Hidden-regime / regime-sliced validation.
- Transaction-cost sensitivity.
- Drawdown-period analysis.
- Signal-family comparison.
- Comparison against buy-and-hold QQQ.

## How This Repo Relates To The Original Submission

The repository has two purposes:

1. Preserve the full research code path in a runnable repo.
2. Document the original challenge methodology and result summaries without
   redistributing challenge-provided data.

The included dataset should therefore be read as the runnable repo dataset,
while the original result summary refers to the actual finalist submission.
Some evidence files were imported later from my private research archive, which
explains why their git timestamps are newer than the project dates.

Supporting summary files:

- [original_challenge_evidence/README.md](original_challenge_evidence/README.md)
- [results/original_challenge_performance_summary.csv](../results/original_challenge_performance_summary.csv)
- [results/original_challenge_signal_family_results.csv](../results/original_challenge_signal_family_results.csv)
- [results/original_challenge_cost_sensitivity.csv](../results/original_challenge_cost_sensitivity.csv)

## Limitations

This remains a research backtest, not a production trading strategy. Important limitations include simplified execution assumptions, simplified transaction costs, lack of full slippage/capacity modeling, possible instability of historical relationships, and the general risk of overfitting in signal research.
