# QQQ Systematic Signal Research

## 1. Research Question

Can a diversified portfolio of simple QQQ timing signals improve out-of-sample risk-adjusted returns relative to buy-and-hold while preserving no-lookahead discipline and explicit transaction-cost modeling?

## 2. Data

The public repository ships with a sanitized sample dataset covering `2018-01-02` through `2025-06-30` with the following minimum schema:

```text
date,qqq_close,qqq_high,qqq_low,dxy_close
```

Because the original full-history private research inputs are not committed, the public artifact pack uses the following reproducible split:

| Split | Start | End |
|---|---|---|
| Train | 2018-01-01 | 2020-12-31 |
| Validation | 2021-01-01 | 2022-12-31 |
| Holdout | 2023-01-01 | 2025-06-30 |

## 3. Method

The repo implements several interpretable signal families:

- trend
- volatility / mean reversion
- defensive volatility
- risk control
- cross-asset macro
- seasonality

Each signal emits daily target exposure in the bounded range `[-1.0, 1.5]`. Exposure is applied to the next day’s close-to-close return, and one-way transaction costs are modeled as a function of turnover.

## 4. Backtest Integrity

- Signal application uses shifted exposures to reduce lookahead risk.
- Validation-period behavior is used for signal selection.
- The holdout period is not used for iterative membership changes in the final ensemble.
- The final public artifact pack is regenerated directly from code via `python -m src.generate_research_artifacts`.

## 5. Model Selection

The final public-sample ensemble is selected by:

1. Ranking each family by validation Sharpe after 5 bps costs.
2. Removing near-duplicate validation profiles.
3. Combining the surviving family representatives in an equal-weight clipped ensemble.

On the committed public sample, the final ensemble contains:

- `medium_term_trend`
- `rsi_deep_value`
- `turn_of_month`

The detailed family ranking is committed in [results/model_selection_summary.csv](../results/model_selection_summary.csv).

## 6. Results

Headline performance from [results/final_performance_summary.csv](../results/final_performance_summary.csv):

| Strategy | Validation Sharpe | Holdout Sharpe | Holdout Total Return | Holdout Max DD | Holdout Ann Vol | Holdout Turnover |
|---|---:|---:|---:|---:|---:|---:|
| Buy & Hold QQQ | 0.26 | -0.45 | -26.0% | -40.1% | 21.0% | 0.00 |
| Medium-Term Trend | 0.65 | 0.02 | -2.9% | -21.0% | 17.4% | 0.09 |
| RSI Deep Value | 0.26 | -0.45 | -39.0% | -54.9% | 31.5% | 0.00 |
| Dual Trend Macro | -0.34 | -0.91 | -40.2% | -44.6% | 19.8% | 0.10 |
| Final Research Ensemble | 0.36 | -0.29 | -17.0% | -31.9% | 18.7% | 0.06 |

Interpretation:

- The public-sample final ensemble improves holdout drawdown relative to buy-and-hold.
- The public-sample holdout Sharpe remains negative, which is a useful reminder that validation success on a small sanitized sample does not guarantee durable out-of-sample alpha.
- The medium-term trend sleeve is the cleanest individual public-sample performer in this version of the repo.

## 7. Robustness

### Cost sensitivity

For the final research ensemble, holdout Sharpe degrades as one-way turnover cost increases:

| Cost | Holdout Sharpe | Holdout Ann Return | Holdout Max DD |
|---|---:|---:|---:|
| 1 bps | -0.26 | -6.4% | -31.2% |
| 5 bps | -0.29 | -6.9% | -31.9% |
| 10 bps | -0.33 | -7.7% | -32.9% |
| 20 bps | -0.41 | -9.1% | -34.8% |

### Parameter sensitivity

The committed parameter-sensitivity grid shows that:

- `medium_term_trend` has the widest response range on holdout (`-0.05` to `0.26` Sharpe).
- `rsi_deep_value` and `turn_of_month` are effectively invariant on the sanitized public sample, indicating the sample is too coarse to stress those sleeves meaningfully.

### Regime analysis

Structural regime summaries in [results/regime_summary.csv](../results/regime_summary.csv) show that the final ensemble:

- holds up better than buy-and-hold in bear/high-vol and bear/low-vol drawdowns
- remains strong in bull/high-vol regimes
- gives up some upside in bull/low-vol regimes in exchange for shallower drawdowns

## 8. Limitations

- The public dataset is sanitized and shorter than the intended full-history research design.
- DXY and cross-asset behavior are only as realistic as the committed public sample.
- Daily close-to-close execution is idealized.
- Costs, slippage, taxes, and borrow are still simplified.
- A stronger public version would use a longer redistributable dataset and more diverse non-duplicate sleeves.

## 9. Relationship to Original Challenge

The results in this public report are generated from the sanitized sample dataset. They are included to demonstrate the reproducibility and mechanics of the codebase.

The original challenge results were generated on a longer private dataset and are summarized separately in [reports/original_challenge_summary.md](original_challenge_summary.md). The public sample-data results are not intended to reproduce the original challenge Sharpe.

## 10. Deliverables

The public repo now includes:

- [results/final_performance_summary.csv](../results/final_performance_summary.csv)
- [results/cost_sensitivity.csv](../results/cost_sensitivity.csv)
- [results/parameter_sensitivity.csv](../results/parameter_sensitivity.csv)
- [results/regime_summary.csv](../results/regime_summary.csv)
- [figures/final_equity_curve.png](../figures/final_equity_curve.png)
- [figures/final_drawdown.png](../figures/final_drawdown.png)
- [figures/rolling_sharpe.png](../figures/rolling_sharpe.png)
- [figures/cost_sensitivity.png](../figures/cost_sensitivity.png)
- [figures/parameter_sensitivity_heatmap.png](../figures/parameter_sensitivity_heatmap.png)
- [figures/regime_breakdown.png](../figures/regime_breakdown.png)
- [notebooks/01_project_report.ipynb](../notebooks/01_project_report.ipynb)
- [reports/original_challenge_summary.md](original_challenge_summary.md)
