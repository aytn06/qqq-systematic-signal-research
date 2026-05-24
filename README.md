# QQQ Systematic Signal Research

I built this repository around my Quanta QR Fellowship finalist project on
systematic QQQ timing. The core idea was simple: instead of holding QQQ at a
fixed 100% allocation, can I adjust exposure day by day with a small set of
interpretable signals and get a cleaner risk/reward profile than buy-and-hold?

This repo is the runnable public version of that work. It includes the signal
definitions, the no-lookahead backtest, the validation-based selection logic,
and the scripts that generate the result tables and figures. The committed
dataset is sanitized so the full pipeline can run end to end without
redistributing the original private challenge data.

## What I Built

- a daily QQQ exposure-allocation pipeline with long, flat, and modest short
  states
- signal sleeves across trend, volatility, oversold mean reversion, cross-asset
  confirmation, and seasonality
- a backtest path that shifts exposures by one day and charges turnover costs
- validation-only model selection for the final public ensemble
- committed CSV and figure outputs so the project can be inspected without
  rerunning everything
- lightweight tests and CI for the public workflow

## Main Question

The research question behind the project is:

> Can a diversified set of simple QQQ timing signals improve out-of-sample
> risk-adjusted performance relative to buy-and-hold, while surviving
> transaction costs and explicit train / validation / holdout discipline?

The project is a research backtest, not a production trading system. The point
is to show the signal design, the validation protocol, and the tradeoffs that
show up once the rules are tested honestly.

## How The Pipeline Works

The daily workflow is straightforward:

1. Load QQQ price and range data plus DXY from the input panel.
2. Compute interpretable features such as moving averages, RSI, Parkinson
   volatility, ATR-style shocks, rolling skew, and month-turn indicators.
3. Map those features into target QQQ exposures in the bounded range
   `[-1.0, 1.5]`.
4. Apply the chosen exposure to the next day's QQQ return rather than the same
   day's return.
5. Charge one-way transaction costs based on absolute exposure changes.
6. Compare signals on validation, build a final ensemble from the surviving
   sleeves, and report holdout performance only after membership is fixed.

The important design choice is that every signal is interpretable. There is no
black-box optimizer hiding behind the scenes. Each sleeve is a direct mapping
from a market state to a target exposure.

## Signal Set

The repo currently includes the following baseline sleeves:

| Signal | Family | What it does |
|---|---|---|
| `long_term_trend` | Trend | Stays strongly long above a long moving average and goes to cash otherwise |
| `medium_term_trend` | Trend | Uses a 50-day EMA for tactical trend exposure |
| `rsi_deep_value` | Vol / mean reversion | Buys deeply oversold selloffs even when volatility is elevated |
| `rsi_gated_short` | Defensive volatility | Allows defensive short exposure but avoids shorting when QQQ is already oversold |
| `conservative_fade` | Defensive volatility | Reduces risk as volatility rises and goes to cash in extreme conditions |
| `vol_shock_dampener` | Risk control | Cuts exposure after unusually large true-range shocks |
| `skew_filter` | Risk control | Avoids shorting when high-volatility returns also skew positive |
| `dual_trend_macro` | Cross-asset macro | Combines QQQ trend with DXY trend to distinguish risk-on from risk-off states |
| `turn_of_month` | Seasonality | Adds exposure around the last and first business days of the month |

Each sleeve outputs a daily target exposure. The project then compares those
exposure paths rather than comparing vague "ideas."

## Original Project And Public Repo

The original finalist project used a longer private QQQ history. This public
repo keeps the pipeline runnable with a sanitized sample instead of trying to
fake a full reproduction from incomplete public inputs.

The original private-run protocol was:

| Split | Dates | Purpose |
|---|---:|---|
| Train | 2000-01-01 to 2015-12-31 | Develop and discard hypotheses |
| Validation | 2016-01-01 to 2021-12-31 | Choose sleeves and build the final ensemble |
| Blind holdout | 2022-01-01 to 2025-06-30 | Final out-of-sample evaluation |

The committed public dataset is shorter, so the public repo uses:

| Public split | Dates | Purpose |
|---|---:|---|
| Train | 2018-01-01 to 2020-12-31 | First-pass signal work |
| Validation | 2021-01-01 to 2022-12-31 | Public-sample model selection |
| Holdout | 2023-01-01 to 2025-06-30 | Final public-sample evaluation |

The public results are therefore best read as:

- a fully runnable research implementation
- an honest public sample of the workflow
- not a claim that the sanitized dataset recreates the original finalist Sharpe

The original challenge summary is documented separately in:

- [reports/original_challenge_summary.md](reports/original_challenge_summary.md)
- [reports/original_challenge_evidence/README.md](reports/original_challenge_evidence/README.md)
- [results/original_challenge_performance_summary.csv](results/original_challenge_performance_summary.csv)

## How I Chose The Final Public Ensemble

I did not pick the final public ensemble by eyeballing holdout Sharpe. The
selection path in [src/generate_research_artifacts.py](src/generate_research_artifacts.py)
uses validation-only information.

The selection logic is:

1. group signals by family
2. rank each family representative using validation Sharpe, validation max
   drawdown, turnover, and cost drag
3. remove near-duplicate validation profiles so the final basket is not just
   several versions of the same exposure path
4. average the surviving sleeves and clip the final ensemble to the allowed
   exposure range

On the committed public sample, the final ensemble contains:

- `medium_term_trend`
- `rsi_deep_value`
- `turn_of_month`

The detailed ranking lives in:

- [results/model_selection_summary.csv](results/model_selection_summary.csv)
- [results/signal_family_results.csv](results/signal_family_results.csv)
- [reports/research_decisions.md](reports/research_decisions.md)

## Public Sample Results

The table below comes from the committed public sample and the default 5 bps
one-way turnover cost assumption.

| Strategy | Validation Sharpe | Holdout Sharpe | Holdout Max DD | Holdout Ann Vol | Holdout Turnover | Cost |
|---|---:|---:|---:|---:|---:|---:|
| Buy & Hold QQQ | 0.26 | -0.45 | -40.1% | 21.0% | 0.00 | 5 bps |
| Medium-Term Trend | 0.65 | 0.02 | -21.0% | 17.4% | 0.09 | 5 bps |
| RSI Deep Value | 0.26 | -0.45 | -54.9% | 31.5% | 0.00 | 5 bps |
| Dual Trend Macro | -0.34 | -0.91 | -44.6% | 19.8% | 0.10 | 5 bps |
| Final Research Ensemble | 0.36 | -0.29 | -31.9% | 18.7% | 0.06 | 5 bps |

The public sample tells a mixed but useful story:

- the final public ensemble reduces holdout drawdown relative to buy-and-hold
- the public holdout Sharpe is still negative
- the medium-term trend sleeve is the cleanest standalone public-sample result

I kept that negative public holdout in the repo on purpose. The project is more
credible with a real tradeoff than it would be with a cleaned-up story that
only kept flattering outputs.

Supporting files:

- [results/final_performance_summary.csv](results/final_performance_summary.csv)
- [results/cost_sensitivity.csv](results/cost_sensitivity.csv)
- [results/parameter_sensitivity.csv](results/parameter_sensitivity.csv)
- [results/regime_summary.csv](results/regime_summary.csv)
- [figures/final_equity_curve.png](figures/final_equity_curve.png)
- [figures/final_drawdown.png](figures/final_drawdown.png)
- [figures/rolling_sharpe.png](figures/rolling_sharpe.png)
- [figures/cost_sensitivity.png](figures/cost_sensitivity.png)
- [figures/parameter_sensitivity_heatmap.png](figures/parameter_sensitivity_heatmap.png)
- [figures/regime_breakdown.png](figures/regime_breakdown.png)

## Data

The pipeline expects at least:

```text
date,qqq_close,qqq_high,qqq_low,dxy_close
```

The committed [data/sample_prices.csv](data/sample_prices.csv) file is a
sanitized public sample covering `2018-01-02` through `2025-06-30`. It exists
so the full pipeline can run locally and in CI. It is not the same thing as the
private full-history dataset used in the original finalist project.

## Run The Project

Create a virtual environment and install in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Then run the baseline workflow:

```bash
python -m src.run_backtest
python -m src.make_plots
python -m src.generate_research_artifacts
pytest
```

The CLI defaults point at the included public sample, so those commands work
without extra arguments.

Console scripts are also installed:

```bash
qqq-backtest
qqq-plots
qqq-artifacts
```

## Repository Layout

```text
.
├── data/                  # Public sample data and input schema notes
├── figures/               # Committed plots from the public sample run
├── notebooks/             # Walkthrough notebook
├── reports/               # Project summaries and supporting notes
├── results/               # Final tables generated from the public sample
├── src/                   # Signal, backtest, metrics, and report-generation code
├── tests/                 # Unit and pipeline smoke tests
├── CONTRIBUTING.md
├── Makefile
├── pyproject.toml
└── README.md
```

## Notes

This repo is most useful as evidence of how I approached the problem:

- define a small, interpretable signal zoo
- backtest with shifted exposures and explicit costs
- separate validation from holdout
- document what survived and what did not

It is not meant to claim that a sanitized public sample fully proves the
original private-run challenge result. It is meant to show the actual research
pipeline behind that project in a form that is runnable and inspectable.
