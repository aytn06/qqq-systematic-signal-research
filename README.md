# QQQ Systematic Signal Research

Research project for building and evaluating interpretable QQQ timing signals with disciplined validation, transaction-cost modeling, and a clean handoff path for GitHub review.

This repo is meant to feel like a real quant research project:

- reproducible Python setup
- documented data contract
- CLI entry points for backtests and plots
- committed public research artifacts
- lightweight test coverage
- GitHub Actions CI for pushes and pull requests

## Reviewer Takeaway

This repository is intended to demonstrate the research process behind the project: clean signal implementation, no-lookahead backtesting, train/validation/holdout separation, transaction-cost modeling, sensitivity analysis, and regime evaluation.

The public sample-data results are not intended to reproduce the original private challenge Sharpe. The original challenge result is documented separately as a preserved summary statistic.

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

## Public Artifact vs. Original Challenge Results

This repository contains a public, sanitized version of the QQQ signal-research framework. The included sample dataset is used to demonstrate the mechanics of the pipeline and to make the code runnable without redistributing private challenge data.

The original Quanta QR Fellowship finalist project used a longer QQQ dataset with the following protocol:

| Split | Dates | Purpose |
|---|---:|---|
| Train | 2000-01-01 to 2015-12-31 | Signal development |
| Validation | 2016-01-01 to 2021-12-31 | Signal selection and ensemble construction |
| Blind holdout | 2022-01-01 to 2025-06-30 | Final out-of-sample evaluation |

The public sample-data results should not be interpreted as the original challenge performance. Original challenge result summaries are documented in:

- [reports/original_challenge_summary.md](reports/original_challenge_summary.md)
- [reports/original_challenge_evidence/README.md](reports/original_challenge_evidence/README.md)
- [results/original_challenge_performance_summary.csv](results/original_challenge_performance_summary.csv)
- [results/original_challenge_signal_family_results.csv](results/original_challenge_signal_family_results.csv)
- [results/original_challenge_cost_sensitivity.csv](results/original_challenge_cost_sensitivity.csv)

## Repository Layout

```text
.
├── data/                  # Input data contract and sanitized public sample
├── figures/               # Committed final figures plus locally generated extras
├── notebooks/             # Polished public notebook and suggested follow-ons
├── reports/               # Short-form project summaries
├── results/               # Committed final tables plus locally generated extras
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
python -m src.generate_research_artifacts
pytest
```

If you install the project in editable mode, these console scripts are also available:

```bash
qqq-backtest
qqq-plots
qqq-artifacts
```

You can override the defaults when using your own dataset:

```bash
python -m src.run_backtest \
  --input data/sample_prices.csv \
  --output results/performance_summary.csv

python -m src.make_plots \
  --input data/sample_prices.csv \
  --output-dir figures

python -m src.generate_research_artifacts \
  --input data/sample_prices.csv \
  --results-dir results \
  --figures-dir figures
```

## Research Design

The full research design this project aims for is:

| Split | Dates | Purpose |
|---|---:|---|
| Train | 2000-01-01 to 2015-12-31 | Develop hypotheses |
| Validation | 2016-01-01 to 2021-12-31 | Select and combine signals |
| Holdout | 2022-01-01 to 2025-06-30 | Final out-of-sample evaluation |

The holdout period should not be used for iterative signal selection.

Because the public repository ships with a shorter sanitized sample dataset rather than the original full-history research inputs, the committed artifact pack uses a reproducible public split:

| Public Split | Dates | Purpose |
|---|---:|---|
| Train | 2018-01-01 to 2020-12-31 | Signal ideation and first-pass filtering |
| Validation | 2021-01-01 to 2022-12-31 | Model selection and ensemble design |
| Holdout | 2023-01-01 to 2025-06-30 | Final evaluation on the public sample |

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

The repo now publishes two ensemble views:

- `equal_weight_ensemble`: baseline average of the full signal zoo
- `final_research_ensemble`: validation-selected blend of the final public-sample sleeves

## Model Selection Protocol

Signals are developed at the individual-sleeve level first and evaluated on the validation window before any final ensemble is formed.

The public artifact pack uses the following selection rules:

1. Group candidate signals by family.
2. Within each family, rank signals with a validation-only score that rewards higher Sharpe and shallower drawdowns while lightly penalizing turnover and cost drag.
3. Remove near-duplicate validation profiles so the final basket is not just the same sleeve repeated under different names.
4. Build the final ensemble from the surviving family representatives and clip exposure to the allowed range.
5. Report holdout metrics only after the ensemble membership is already fixed.

On the current public sample, this produces a final ensemble composed of:

- `medium_term_trend`
- `rsi_deep_value`
- `turn_of_month`

The selection summary is committed in [results/model_selection_summary.csv](results/model_selection_summary.csv) and the per-family comparison lives in [results/signal_family_results.csv](results/signal_family_results.csv).

## Headline Results

The committed results below come from the reproducible public sample split and the default 5 bps one-way turnover cost assumption.

| Strategy | Validation Sharpe | Holdout Sharpe | Holdout Max DD | Holdout Ann Vol | Holdout Turnover | Cost |
|---|---:|---:|---:|---:|---:|---:|
| Buy & Hold QQQ | 0.26 | -0.45 | -40.1% | 21.0% | 0.00 | 5 bps |
| Medium-Term Trend | 0.65 | 0.02 | -21.0% | 17.4% | 0.09 | 5 bps |
| RSI Deep Value | 0.26 | -0.45 | -54.9% | 31.5% | 0.00 | 5 bps |
| Dual Trend Macro | -0.34 | -0.91 | -44.6% | 19.8% | 0.10 | 5 bps |
| Final Research Ensemble | 0.36 | -0.29 | -31.9% | 18.7% | 0.06 | 5 bps |

Two things are important here:

- The public-sample final ensemble improves holdout drawdown versus the benchmark (`-31.9%` vs `-40.1%`).
- It still fails to produce a positive holdout Sharpe on the committed public sample, which is exactly the kind of non-cherry-picked result worth showing in a serious research repo.

See the committed artifact pack for the supporting tables and figures:

- [results/final_performance_summary.csv](results/final_performance_summary.csv)
- [results/cost_sensitivity.csv](results/cost_sensitivity.csv)
- [results/parameter_sensitivity.csv](results/parameter_sensitivity.csv)
- [results/regime_summary.csv](results/regime_summary.csv)
- [figures/final_equity_curve.png](figures/final_equity_curve.png)
- [figures/final_drawdown.png](figures/final_drawdown.png)
- [figures/rolling_sharpe.png](figures/rolling_sharpe.png)
- [figures/signal_correlation_heatmap.png](figures/signal_correlation_heatmap.png)
- [figures/cost_sensitivity.png](figures/cost_sensitivity.png)
- [figures/parameter_sensitivity_heatmap.png](figures/parameter_sensitivity_heatmap.png)
- [figures/regime_breakdown.png](figures/regime_breakdown.png)

## Data Contract

The pipeline expects at least these columns:

```text
date,qqq_close,qqq_high,qqq_low,dxy_close
```

Optional future columns can include:

```text
qqq_volume,spy_close,vix_close,tlt_close,rates_10y
```

The included `data/sample_prices.csv` is a sanitized public sample spanning `2018-01-02` through `2025-06-30`. It is useful for validating the mechanics of the repo and for shipping a reproducible public artifact pack, but it is not the same thing as the private full-history research dataset that originally motivated the project.

Do not commit proprietary or licensed market data. Use [data/README.md](data/README.md) to document local datasets instead.

## Public Artifact Pack

The repo now includes a committed public-facing artifact pack so reviewers do not need to run the code just to understand the project:

- [notebooks/01_project_report.ipynb](notebooks/01_project_report.ipynb): polished walk-through notebook
- [reports/final_project_report.md](reports/final_project_report.md): concise research memo
- [results/public_data_split.csv](results/public_data_split.csv): exact split boundaries used for the public sample
- final summary, cost, parameter, and regime CSV outputs in `results/`
- final plots in `figures/`

## Developer Workflow

The repo includes a small but practical development loop:

- `Makefile` for common setup and run commands
- `pytest` smoke tests for data loading, metrics, and backtest mechanics
- GitHub Actions CI in `.github/workflows/ci.yml`

Recommended loop:

1. Add or adjust one signal family at a time.
2. Re-run the backtest summary.
3. Re-generate the public artifact pack.
4. Run tests before pushing.
5. Preserve holdout discipline.

## Current Limitations

- Daily close-to-close execution is idealized.
- Transaction costs are simplified to one-way turnover costs.
- Borrow, slippage, taxes, and capacity are not modeled.
- The package name is intentionally lightweight and geared toward repo ergonomics, not distribution polish.
- The public sample is sanitized and shorter than the original research ambition.
- Some sleeves are piecewise-constant on the public sample, which makes parameter sensitivity less informative than it would be on a richer dataset.

## Good Next Steps

- Swap the public sample for a redistributable historical dataset with the full intended train/validation/holdout span.
- Expand the signal zoo with truly distinct macro and volatility sleeves.
- Add richer cost models, slippage assumptions, and explicit rebalance constraints.
- Add notebook outputs or a rendered report artifact for easier browser-only review.

## Resume-Friendly Summary

> Built a systematic QQQ signal-research pipeline with strict train/validation/holdout separation, no-lookahead backtesting, transaction-cost modeling, regime-aware evaluation, and GitHub-ready project scaffolding.
