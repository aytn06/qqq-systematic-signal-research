# One-Page Project Summary: QQQ Systematic Signal Research

Note: This one-page summary describes the original challenge protocol. The repository also includes a smaller sanitized sample dataset for reproducibility of the code mechanics. Included sample-data results are not intended to match the original private challenge results.

## Objective

Build and validate a systematic QQQ allocation strategy using prespecified signal families, strict train/validation/blind-holdout separation, transaction-cost modeling, and regime analysis.

## Data

Daily QQQ close/high/low data plus cross-asset features such as DXY. The repo includes only a sanitized sample dataset for reproducibility. Actual research data should be stored locally and documented in `data/README.md`.

## Method

Each signal maps daily information into a target exposure between -1.0 and 1.5. Signals are grouped by family: trend, volatility, mean reversion, cross-asset macro, defensive overlays, and seasonality. Exposures are shifted before applying next-day returns to reduce look-ahead risk.

## Validation

- Train: 2000–2015
- Validation: 2016–2021
- Blind holdout: 2022–Jun 2025
- ±10% parameter sensitivity
- Transaction-cost sensitivity
- Regime-sliced performance
- Signal-correlation analysis

## Main Risks

- Overfitting from many signal trials.
- Close-to-close execution assumptions.
- Simplified transaction costs and slippage.
- Historical instability of cross-asset relationships.
- Repeated holdout peeking.

## Interview Pitch

I used LLMs for hypothesis generation, but the core project was building a disciplined quant research pipeline: clean signal implementation, no-lookahead validation, train/validation/holdout separation, transaction-cost modeling, and robustness analysis. The goal was not simply to maximize Sharpe; it was to test whether a diverse set of interpretable QQQ signals could survive realistic validation checks.
