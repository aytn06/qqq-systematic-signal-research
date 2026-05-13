# QQQ Systematic Signal Research

Research project for building and evaluating interpretable QQQ timing signals with disciplined validation, transaction-cost modeling, and a clean handoff path for GitHub review.

This repo is meant to feel like a real quant research project:

- reproducible Python setup
- documented data contract
- CLI entry points for backtests and plots
- lightweight test coverage
- GitHub Actions CI for pushes and pull requests

## What This Project Does

The central question is:

> Can a diversified set of simple, interpretable QQQ timing signals improve out-of-sample risk-adjusted performance relative to buy-and-hold QQQ?

The project focuses on process quality as much as raw Sharpe:

- no-lookahead signal application
- explicit train / validation / holdout periods
- transaction-cost drag
- parameter sensitivity checks
- regime-aware analysis

This is a research backtest, not a production trading system.

## Repository Layout

```text
.
├── data/                  # Input data contract and synthetic smoke-test dataset
├── figures/               # Generated plots (gitignored, tracked via README)
├── notebooks/             # Suggested exploratory notebook workflow
├── reports/               # Short-form project summaries
├── results/               # Generated tables and summaries (gitignored, tracked via README)
├── src/                   # Core research package
├── tests/                 # Unit and smoke tests
├── CONTRIBUTING.md        # Workflow and contribution guidance
├── Makefile               # Common developer commands
├── pyproject.toml         # Project metadata and optional editable install
└── README.md
```

## Quickstart

Create a virtual environment and install the project in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

If you prefer a plain requirements install:

```bash
pip install -r requirements.txt
```

## Run The Pipeline

The CLI defaults point at the included sample dataset, so the shortest path is:

```bash
python -m src.run_backtest
python -m src.make_plots
pytest
```

If you install the project in editable mode, these console scripts are also available:

```bash
qqq-backtest
qqq-plots
```

You can override the defaults when using your own dataset:

```bash
python -m src.run_backtest \
  --input data/sample_prices.csv \
  --output results/performance_summary.csv

python -m src.make_plots \
  --input data/sample_prices.csv \
  --output-dir figures
```

## Research Design

The default validation windows are:

| Split | Dates | Purpose |
|---|---:|---|
| Train | 2000-01-01 to 2015-12-31 | Develop hypotheses |
| Validation | 2016-01-01 to 2021-12-31 | Select and combine signals |
| Holdout | 2022-01-01 to 2025-06-30 | Final out-of-sample evaluation |

The holdout period should not be used for iterative signal selection.

## Included Signal Families

The current baseline signal set includes:

| Signal | Family | Description |
|---|---|---|
| `long_term_trend` | Trend | Long when QQQ is above a long moving average |
| `medium_term_trend` | Trend | Medium-horizon tactical trend signal |
| `rsi_deep_value` | Vol / mean reversion | Buys deeply oversold, high-volatility selloffs |
| `rsi_gated_short` | Defensive | Avoids shorting into already oversold conditions |
| `conservative_fade` | Defensive | Reduces risk during extreme volatility |
| `vol_shock_dampener` | Risk control | Cuts exposure after unusually large true-range shocks |
| `skew_filter` | Risk control | Avoids shorting when high-volatility returns skew positive |
| `dual_trend_macro` | Cross-asset | Combines QQQ trend with DXY trend |
| `turn_of_month` | Seasonality | Adds risk around month-turn behavior |

The current ensemble is deliberately simple: equal-weight the signal zoo, then clip exposure to the allowed range.

## Data Contract

The pipeline expects at least these columns:

```text
date,qqq_close,qqq_high,qqq_low,dxy_close
```

Optional future columns can include:

```text
qqq_volume,spy_close,vix_close,tlt_close,rates_10y
```

The included `data/sample_prices.csv` is synthetic smoke-test data spanning `2018-01-01` through `2025-06-30`. It is useful for validating the mechanics of the repo, not for making real research claims.

Do not commit proprietary or licensed market data. Use [data/README.md](data/README.md) to document local datasets instead.

## Developer Workflow

The repo includes a small but practical development loop:

- `Makefile` for common setup and run commands
- `pytest` smoke tests for data loading, metrics, and backtest mechanics
- GitHub Actions CI in `.github/workflows/ci.yml`

Recommended loop:

1. Add or adjust one signal family at a time.
2. Re-run the backtest summary.
3. Re-generate figures.
4. Run tests before pushing.
5. Preserve holdout discipline.

## Current Limitations

- Daily close-to-close execution is idealized.
- Transaction costs are simplified to one-way turnover costs.
- Borrow, slippage, taxes, and capacity are not modeled.
- The package name is intentionally lightweight and geared toward repo ergonomics, not distribution polish.
- Sample data is synthetic and only validates mechanics.

## Good Next Steps

- Add richer signal families and more formal model selection rules.
- Expand sensitivity-analysis coverage into tests or notebooks.
- Add notebook examples for signal ideation and regime attribution.
- Replace synthetic sample data with a documented local research dataset.

## Resume-Friendly Summary

> Built a systematic QQQ signal-research pipeline with strict train/validation/holdout separation, no-lookahead backtesting, transaction-cost modeling, regime-aware evaluation, and GitHub-ready project scaffolding.
