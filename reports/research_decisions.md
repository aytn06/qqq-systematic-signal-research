# Project Notes

I kept this note to record the decisions that shaped the committed version of
the QQQ project. The goal is not to present a polished story after the fact. It
is to keep track of what changed once the backtests, validation results, and
report-generation path were inspected more carefully.

## Included Dataset And Original Challenge Run

The original finalist submission used a longer dataset provided through the
Quanta QR Fellowship challenge. This repo ships with an included dataset
covering `2018-01-02` through `2025-06-30` so the code can run end to end
without reposting challenge data. That split forced the project into two
layers:

- a runnable pipeline generated from the included repo dataset
- a separate summary of the original finalist result on the challenge dataset

I assembled the GitHub repo later from my private research archive, which is
why some summaries and supporting notes have newer commit dates than the
original project itself.

## Shifted Exposure Became The Default

The backtest applies today's chosen exposure to the next day's return. That
choice is slightly harsher on performance, but it makes the pipeline much easier
to defend because the exposure path does not reuse same-day information.

## Family Diversity Mattered More Than Raw Signal Count

Several sleeves had different names but very similar validation behavior. On the
included sample, the main example was the cluster around:

- `conservative_fade`
- `rsi_gated_short`
- `skew_filter`

Those sleeves moved too much like `rsi_deep_value` to justify all of them
surviving into the final ensemble. The committed version therefore keeps one strong
representative instead of pretending multiple near-duplicates are independent
ideas.

## Cross-Asset Confirmation Stayed In The Comparison Set

`dual_trend_macro` stayed in the committed outputs because it captures a real
part of the research question: whether QQQ timing improves when price trend is
checked against a broad dollar signal. It was not selected into the final
ensemble because its validation ranking lagged the sleeves that survived.

## Holdout Leakage Was Removed

An earlier report-generation pass let holdout information influence the
selection path. The committed version fixes that. The final ensemble is
now ranked only on:

- validation Sharpe
- validation max drawdown
- validation turnover
- validation cost drag

Holdout metrics are still reported, but they are no longer used to choose which
signals survive.

## The Negative Holdout Was Left In Place

The included-dataset final ensemble does not have a positive holdout Sharpe. I left
that result in the repo because the project is supposed to show the research
process honestly, not quietly swap in a prettier sample after the fact.

## Evidence For The Original Challenge Result Is Still Limited

The repo has a dedicated folder at `reports/original_challenge_evidence/` for
recovered screenshots, PDFs, notebooks, or old output tables. Right now, the
original Quanta result is still documented mostly as a preserved summary rather
than a fully reproduced evidence trail. That is an evidence gap, and the repo
states it directly instead of smoothing it over.
