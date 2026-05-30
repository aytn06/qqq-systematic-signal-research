# QQQ Systematic Signal Research

I built this project during the Quanta QR Fellowship finalist process. The
question was simple: instead of holding QQQ at a fixed weight all the time, can
I change exposure day by day with a small set of clear rules and get a better
risk profile than buy-and-hold?

That is what this repo does. It contains the signal rules, the backtest, the
validation logic, the result tables, and the plots.

The original finalist submission used QQQ data provided through the challenge,
so I cannot post that dataset here. To make the project runnable, I included a
smaller dataset with the same basic schema. The research came first and the
GitHub repo was assembled later from my private research archive, which is why
some supporting files have newer commit dates than the project itself.

## What The Project Does

Each day the project chooses a target QQQ exposure in the range `[-1.0, 1.5]`.
That means the strategy can be short, flat, long, or slightly leveraged long.
The rules are deliberately simple. They are based on things like:

- trend
- oversold conditions
- volatility
- dollar strength through DXY
- month-end seasonality

The point was not to build a black-box model. The point was to see whether a
small set of understandable signals could survive a careful research process.

## How It Works

The workflow is:

1. Load QQQ close, high, low, and DXY.
2. Build features such as moving averages, RSI, range-based volatility, shock
   measures, skew, and calendar indicators.
3. Turn those features into daily exposure rules.
4. Apply today's chosen exposure to tomorrow's QQQ return.
5. Charge transaction costs when exposure changes.
6. Select the final ensemble using validation only, then report holdout
   results.

That one-day shift is important. It keeps the backtest from using same-day
information twice.

## Signals

The current signal set includes:

| Signal | Idea |
|---|---|
| `long_term_trend` | stay long when QQQ is above a long moving average |
| `medium_term_trend` | use a faster trend rule for tactical exposure |
| `rsi_deep_value` | buy sharp oversold selloffs |
| `rsi_gated_short` | allow defensive shorting, but avoid shorting a deeply oversold market |
| `conservative_fade` | reduce risk as volatility rises |
| `vol_shock_dampener` | cut exposure after unusually large range shocks |
| `skew_filter` | avoid shorting when return skew is strongly positive |
| `dual_trend_macro` | combine QQQ trend with DXY trend |
| `turn_of_month` | add exposure around month-end and the start of the next month |

## The Original Submission And The Included Dataset

The original submission used a longer QQQ history provided through the Quanta
challenge. I cannot redistribute that source data here.

The included repo dataset is shorter, so the repo uses this split:

| Split | Dates | Purpose |
|---|---:|---|
| Train | 2018-01-01 to 2020-12-31 | first-pass work |
| Validation | 2021-01-01 to 2022-12-31 | choose signals and build the ensemble |
| Holdout | 2023-01-01 to 2025-06-30 | final out-of-sample check |

The original challenge protocol was:

| Split | Dates | Purpose |
|---|---:|---|
| Train | 2000-01-01 to 2015-12-31 | develop and discard ideas |
| Validation | 2016-01-01 to 2021-12-31 | choose signals and build the ensemble |
| Blind holdout | 2022-01-01 to 2025-06-30 | final evaluation |

So this repo should be read in two layers:

- it contains the full code path for the project
- it documents the original finalist result separately from the included
  runnable dataset

The original-result notes are here:

- [reports/original_challenge_summary.md](reports/original_challenge_summary.md)
- [reports/original_challenge_evidence/README.md](reports/original_challenge_evidence/README.md)
- [results/original_challenge_performance_summary.csv](results/original_challenge_performance_summary.csv)

## Final Ensemble

I did not choose the final ensemble by looking at holdout Sharpe. The selection
path uses validation only.

On the included dataset, the final ensemble is:

- `medium_term_trend`
- `rsi_deep_value`
- `turn_of_month`

The ranking details are in:

- [results/model_selection_summary.csv](results/model_selection_summary.csv)
- [results/signal_family_results.csv](results/signal_family_results.csv)
- [reports/research_decisions.md](reports/research_decisions.md)

## Results On The Included Dataset

Here are the main 5 bps one-way cost results from the included dataset:

| Strategy | Validation Sharpe | Holdout Sharpe | Holdout Max DD | Holdout Ann Vol | Holdout Turnover |
|---|---:|---:|---:|---:|---:|
| Buy & Hold QQQ | 0.26 | -0.45 | -40.1% | 21.0% | 0.00 |
| Medium-Term Trend | 0.65 | 0.02 | -21.0% | 17.4% | 0.09 |
| RSI Deep Value | 0.26 | -0.45 | -54.9% | 31.5% | 0.00 |
| Dual Trend Macro | -0.34 | -0.91 | -44.6% | 19.8% | 0.10 |
| Final Research Ensemble | 0.36 | -0.29 | -31.9% | 18.7% | 0.06 |

The main takeaway is straightforward. On the included dataset, the final
ensemble helps drawdown relative to buy-and-hold, but it does not produce a
positive holdout Sharpe. I left that in the repo because I would rather show
the actual outcome than smooth it over.

Useful result files:

- [results/final_performance_summary.csv](results/final_performance_summary.csv)
- [results/cost_sensitivity.csv](results/cost_sensitivity.csv)
- [results/parameter_sensitivity.csv](results/parameter_sensitivity.csv)
- [results/regime_summary.csv](results/regime_summary.csv)
- [figures/final_equity_curve.png](figures/final_equity_curve.png)
- [figures/final_drawdown.png](figures/final_drawdown.png)
- [figures/rolling_sharpe.png](figures/rolling_sharpe.png)

## Data

The minimum input schema is:

```text
date,qqq_close,qqq_high,qqq_low,dxy_close
```

The included file [data/sample_prices.csv](data/sample_prices.csv) covers
`2018-01-02` through `2025-06-30`. It is there so the whole pipeline can run in
the repo. It is not the same dataset used in the original finalist submission.

## Run The Project

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
python -m src.run_backtest
python -m src.make_plots
python -m src.build_reports
pytest
```

The defaults point to the included dataset, so the commands work as written.

## What This Repo Is Good For

This repo is best read as a clean record of the research process:

- simple signal design
- no-lookahead backtesting
- validation and holdout separation
- explicit transaction costs
- honest reporting when the included dataset is weaker than the original
  challenge result

It is a research project, not a production trading system.
