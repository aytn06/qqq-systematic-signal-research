# Figures

Committed visual artifacts in this repo:

- `final_equity_curve.png`: benchmark and final ensemble equity curves
- `final_drawdown.png`: buy-and-hold versus final-ensemble drawdown comparison
- `rolling_sharpe.png`: rolling Sharpe comparison for the benchmark and final ensemble
- `signal_correlation_heatmap.png`: correlation heatmap for the selected public-sample sleeves
- `cost_sensitivity.png`: holdout performance across one-way cost assumptions
- `parameter_sensitivity_heatmap.png`: holdout sensitivity of selected sleeves to +/- 10% parameter changes
- `regime_breakdown.png`: structural and event-window regime comparison for the benchmark and final ensemble

Additional exploratory figures such as `equity_curves.png`, `ensemble_drawdown.png`, and `signal_correlation.png` are kept because they were used during the public packaging pass and are still useful for quick manual review.

Regenerate the public artifact pack with:

```bash
python -m src.generate_research_artifacts
```
