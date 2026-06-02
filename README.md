# QQQ Systematic Signal Research

I built this project during the Quanta QR Fellowship finalist process. The
basic question was simple: instead of holding QQQ the same way every day, can I
change exposure with a small set of clear rules and get a better ride than just
buying and holding it?

That is what this repo does. It has the signal rules, the backtest, the
selection logic, the result tables, and the plots.

The original finalist submission used QQQ data provided through the challenge,
so I cannot post that dataset here. To make the project runnable, I included a
smaller dataset with the same basic schema. The research came first and the
GitHub repo was assembled later from my private research archive, which is why
some supporting files have newer commit dates than the project itself.

## The Idea

Each day the project chooses a target QQQ exposure in the range `[-1.0, 1.5]`.
That means the strategy can be short, flat, long, or slightly leveraged long.
The rules are deliberately simple. They are based on things like:

- trend
- oversold conditions
- volatility
- dollar strength through DXY
- month-end seasonality

I was not trying to build a black-box model. I wanted to see whether a small
set of understandable signals could hold up under a disciplined test.

## How I Tested It

The workflow is:

1. Load QQQ close, high, low, and DXY.
2. Build features such as moving averages, RSI, range-based volatility, shock
   measures, skew, and calendar indicators.
3. Turn those features into daily exposure rules.
4. Apply today's chosen exposure to tomorrow's QQQ return.
5. Charge transaction costs when exposure changes.
6. Select the final ensemble using validation only, then report holdout
   results.
7. Re-run the selection idea across multiple expanding walk-forward folds,
   leave the portfolio flat when no signal survives the validation filters,
   and break the final ensemble into component-level return contributions.

That one-day shift matters. It keeps the backtest from double-counting today's
information.

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

## Data And Split

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

I kept the repo runnable by including a smaller dataset with the same basic
schema, and I kept the original challenge notes separately:

- [reports/original_challenge_summary.md](reports/original_challenge_summary.md)
- [reports/original_challenge_evidence/README.md](reports/original_challenge_evidence/README.md)
- [results/original_challenge_performance_summary.csv](results/original_challenge_performance_summary.csv)

## Final Ensemble

I did not choose the final ensemble by peeking at holdout Sharpe. The selection
path uses validation only.

On the included dataset, the final ensemble is:

- `medium_term_trend`
- `rsi_deep_value`
- `turn_of_month`

The ranking details are in:

- [results/model_selection_summary.csv](results/model_selection_summary.csv)
- [results/signal_family_results.csv](results/signal_family_results.csv)
- [reports/research_decisions.md](reports/research_decisions.md)

I also kept the repeated walk-forward selection strict. If a fold has no signal
with positive validation performance after the correlation and duplication
filters, I leave the portfolio flat instead of stuffing extra signals into it.

## Results

Here are the main 5 bps one-way cost results from the included dataset:

| Strategy | Validation Sharpe | Holdout Sharpe | Holdout Max DD | Holdout Ann Vol | Holdout Turnover |
|---|---:|---:|---:|---:|---:|
| Buy & Hold QQQ | 0.26 | -0.45 | -40.1% | 21.0% | 0.00 |
| Medium-Term Trend | 0.65 | 0.02 | -21.0% | 17.4% | 0.09 |
| RSI Deep Value | 0.26 | -0.45 | -54.9% | 31.5% | 0.00 |
| Dual Trend Macro | -0.34 | -0.91 | -44.6% | 19.8% | 0.10 |
| Final Research Ensemble | 0.36 | -0.29 | -31.9% | 18.7% | 0.06 |

The main takeaway is simple. On the included dataset, the final ensemble cuts
drawdown relative to buy-and-hold, but it does not deliver a positive holdout
Sharpe. I left that in because I would rather show the real outcome than clean
it up for presentation.

I also added a moving-block bootstrap summary for the holdout period. It does
not make the result look better. It just shows the uncertainty more honestly.
On the included dataset, the selected ensemble has only about a 30% bootstrap
probability of positive holdout Sharpe.

Useful result files:

- [results/final_performance_summary.csv](results/final_performance_summary.csv)
- [results/cost_sensitivity.csv](results/cost_sensitivity.csv)
- [results/parameter_sensitivity.csv](results/parameter_sensitivity.csv)
- [results/regime_summary.csv](results/regime_summary.csv)
- [results/holdout_bootstrap_summary.csv](results/holdout_bootstrap_summary.csv)
- [results/walkforward_performance.csv](results/walkforward_performance.csv)
- [results/component_attribution_summary.csv](results/component_attribution_summary.csv)
- [figures/final_equity_curve.png](figures/final_equity_curve.png)
- [figures/final_drawdown.png](figures/final_drawdown.png)
- [figures/rolling_sharpe.png](figures/rolling_sharpe.png)
- [figures/walkforward_selection.png](figures/walkforward_selection.png)
- [figures/component_contributions.png](figures/component_contributions.png)

## Input Format

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

What I want someone to take from the repo is that the process is easy to follow.
The rules are simple, the exposure is applied one day later, the ensemble is
chosen on validation rather than holdout, and the weaker included holdout
result is still shown plainly.

This is a research project, not a production trading system.
