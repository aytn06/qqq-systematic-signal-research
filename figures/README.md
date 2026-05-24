# Figures

These are the main plots generated from the committed public sample:

- `final_equity_curve.png`: buy-and-hold, selected sleeves, and final ensemble
- `final_drawdown.png`: drawdown comparison between buy-and-hold and the final
  ensemble
- `rolling_sharpe.png`: rolling Sharpe comparison for the benchmark and final
  ensemble
- `signal_correlation_heatmap.png`: validation-period correlation across the
  selected sleeves
- `cost_sensitivity.png`: how holdout performance moves as one-way cost
  assumptions change
- `parameter_sensitivity_heatmap.png`: +/- 10% parameter perturbation results
- `regime_breakdown.png`: structural and event-window regime comparisons

Some extra exploratory figures are also kept in the folder because they were
useful while building the public report and they still help when reviewing the
strategy paths by hand.

Regenerate the figure set with:

```bash
python -m src.generate_research_artifacts
```
