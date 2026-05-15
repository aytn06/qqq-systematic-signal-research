# Research Decisions

This note captures the concrete decisions that shaped the committed public version of the project. The goal is to preserve some of the day-to-day research tradeoffs rather than only the cleaned final artifact pack.

## 1. Public Sample Framing

The original challenge used a longer private dataset, while the public repo ships with a sanitized `2018-01-02` through `2025-06-30` sample. That forced a split between:

- a reproducible public artifact pack that anyone can run locally
- a separately documented original challenge summary that is not reproduced from raw private data

This is why the repo keeps both:

- `results/final_performance_summary.csv` for the public sample
- `reports/original_challenge_summary.md` for the private-run summary

## 2. Shifted Exposure Became the Default

The backtest path applies exposure to the next return rather than the same-day return. That choice is conservative and slightly worsens some headline metrics, but it reduces accidental lookahead bias and makes the repo easier to defend under review.

## 3. Family Diversity Mattered More Than Signal Count

Several sleeves looked different by name but behaved almost identically on validation. In particular:

- `conservative_fade`
- `rsi_gated_short`
- `skew_filter`

all tracked closely with `rsi_deep_value` on the public sample. The final public ensemble therefore keeps the strongest representative instead of including multiple near-duplicates.

## 4. Cross-Asset Macro Stayed in the Comparison Set

`dual_trend_macro` stayed in the committed outputs because it is useful to show that the project tested cross-asset confirmation ideas rather than only price-derived sleeves. It was not selected into the final public ensemble because its validation-only ranking lagged the surviving family representatives.

## 5. Holdout Leakage Was Removed

An earlier artifact-generation pass used holdout information in the selection path. The committed version fixes that. The final public ensemble is now chosen with a validation-only score based on:

- validation Sharpe
- validation max drawdown
- validation turnover
- validation cost drag

Holdout metrics are still reported, but they are no longer used to rank or select sleeves.

## 6. The Public Holdout Result Was Left Intact

The public-sample final ensemble has a negative holdout Sharpe. That is not flattering, but it is informative. The repo keeps that result because the point of the public project is to demonstrate disciplined research mechanics, not to backfill a prettier story after the fact.

## 7. Evidence for the Original Challenge Is Still Incomplete

The repo now has a dedicated folder at `reports/original_challenge_evidence/` for recovered screenshots, notebooks, PDFs, or other supporting artifacts. No private-run evidence file is committed yet, so the original Quanta result remains documented as a preserved summary statistic rather than a fully reproduced public result.
