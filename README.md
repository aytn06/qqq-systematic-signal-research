# Systematic Signal Research Pipeline for QQQ

## Objective

This project studies whether a diversified portfolio of QQQ timing signals can improve out-of-sample risk-adjusted performance relative to buy-and-hold QQQ.

The core research question is:

> Can a disciplined signal-research pipeline, using train/validation/blind-holdout separation, no-lookahead checks, transaction-cost modeling, and regime analysis, produce a robust QQQ allocation strategy?

This repository is designed as a research-grade implementation of a quant signal pipeline, not as a production trading system.

## Research Design

The project uses a strict train / validation / blind-holdout protocol:

| Split | Dates | Purpose |
|---|---:|---|
| Train | 2000-01-01 to 2015-12-31 | Develop signal hypotheses |
| Validation | 2016-01-01 to 2021-12-31 | Select and combine signals |
| Blind holdout | 2022-01-01 to 2025-06-30 | Final out-of-sample evaluation |

The final holdout period should not be used for signal development or model selection.

## Signal Families

The pipeline supports signals from several prespecified families:

- Trend-following
- Mean reversion
- Volatility / risk regime
- Cross-asset macro signals
- Defensive and short-bias overlays
- Seasonality / flow effects

The current starter implementation includes representative signals:

| Signal | Family | Description |
|---|---|---|
| `long_term_trend` | Trend | Long when QQQ is above long moving average |
| `medium_term_trend` | Trend | Tactical trend using medium moving average |
| `rsi_deep_value` | Mean reversion / vol | Buys aggressively after oversold high-volatility selloffs |
| `rsi_gated_short` | Defensive | Avoids shorting when QQQ is already deeply oversold |
| `conservative_fade` | Defensive | Goes to cash in extreme volatility |
| `vol_shock_dampener` | Risk control | Cuts leverage after large true-range shocks |
| `dual_trend_macro` | Cross-asset | Combines QQQ trend with DXY trend |
| `turn_of_month` | Seasonality | Higher exposure near month-turn windows |

These signals are intentionally simple and interpretable. The value of the project comes from the validation framework, robustness checks, and portfolio combination discipline.

## Role of LLM Assistance

LLMs can be used for brainstorming candidate hypotheses and expanding the search space. However, all final signals should be reimplemented in a controlled Python framework, checked for look-ahead bias, evaluated with train/validation/holdout separation, and stress-tested through parameter sensitivity and regime analysis.

The important research contribution is not "an LLM generated alpha." The important contribution is the disciplined process:

1. Generate hypotheses.
2. Reimplement them cleanly.
3. Validate without look-ahead bias.
4. Stress-test parameters.
5. Combine signals using validation-period behavior.
6. Evaluate once on the blind holdout.

## Backtest Assumptions

- Daily close-to-close returns.
- Exposure is chosen using information available up to time `t`.
- The position is applied to the next close-to-close return.
- Exposure is clipped to the interval `[-1.0, 1.5]`.
- No stop losses.
- Transaction costs are modeled as a one-way cost on changes in exposure.
- The default cost is 5 bps per unit turnover.

The implementation uses `signal.shift(1)` before applying exposure to returns. This is conservative and helps avoid accidental look-ahead bias.

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the main backtest using sample data:

```bash
python -m src.run_backtest --input data/sample_prices.csv --output results/performance_summary.csv
```

Generate plots:

```bash
python -m src.make_plots --input data/sample_prices.csv --output-dir figures
```

Run basic tests:

```bash
pytest tests/
```

## Expected Input Format

The pipeline expects a CSV with at least:

```text
date, qqq_close, qqq_high, qqq_low, dxy_close
```

Optional columns can be added later:

```text
qqq_volume, vix_close, tlt_close, spy_close, rates_10y, etc.
```

Raw proprietary or paid data should not be committed to this repository. Use `data/README.md` to document the source and format. Include only small sample files if needed.

## Results to Report

For each strategy and split, report:

- Annualized return
- Annualized volatility
- Sharpe ratio
- Max drawdown
- Calmar ratio
- Turnover
- Transaction-cost drag
- Exposure distribution
- Regime-sliced performance

A final research table should compare:

| Strategy | Validation Sharpe | Holdout Sharpe | Max DD | Turnover | Cost Assumption |
|---|---:|---:|---:|---:|---:|
| Buy and hold QQQ | TBD | TBD | TBD | 0 | 0 bps |
| Simple trend | TBD | TBD | TBD | TBD | 5 bps |
| Volatility strategy | TBD | TBD | TBD | TBD | 5 bps |
| Ensemble | TBD | TBD | TBD | TBD | 5 bps |

## Robustness Checks

The repo includes hooks for:

- ±10% parameter sensitivity.
- Transaction-cost sensitivity.
- Regime-sliced evaluation.
- Signal correlation analysis.
- Drawdown-period attribution.
- Train/validation/holdout comparison.

## Limitations

This is a research backtest, not a production trading strategy.

Important limitations:

- Results depend on data quality and adjustment methodology.
- Daily close execution is idealized.
- Transaction costs are simplified.
- Slippage, borrow costs, spread effects, taxes, and capacity are not fully modeled.
- Historical relationships may decay.
- Signal selection must avoid repeated holdout peeking.

## Resume Positioning

A concise resume description:

> Built a systematic QQQ signal-research and portfolio-construction pipeline with strict train/validation/blind-holdout separation, no-lookahead checks, transaction-cost modeling, regime-sliced validation, and parameter sensitivity tests.
