# Results

This folder holds the result tables generated from the included dataset.

Main files:

- `final_performance_summary.csv`: the benchmark, representative sleeves, and
  final ensemble comparison
- `model_selection_summary.csv`: validation-only ranking and final ensemble
  membership
- `signal_family_results.csv`: family-level representative table
- `cost_sensitivity.csv`: holdout performance under different one-way cost
  assumptions
- `parameter_sensitivity.csv`: +/- 10% parameter perturbations for the selected
  sleeves
- `regime_summary.csv`: structural and event-window regime breakdowns
- `holdout_bootstrap_summary.csv`: moving-block bootstrap ranges for holdout
  Sharpe, annual return, and drawdown
- `component_attribution_summary.csv`: split-by-split contribution summary for
  the selected ensemble members
- `ensemble_component_contributions.csv`: daily net contribution series for the
  selected ensemble members
- `exposure_state_summary.csv`: time spent short, flat, long, and levered long
- `walkforward_performance.csv`: repeated expanding-window selection results
- `walkforward_selection.csv`: which signals were chosen in each walk-forward
  fold

The walk-forward files keep the selection strict. If no signal survives the
validation filters in a fold, the walk-forward portfolio stays flat rather than
filling the basket with convenience picks.
- `public_data_split.csv`: exact train / validation / holdout dates used for
  the included dataset

The folder also keeps summary files for the original private challenge run:

- `original_challenge_performance_summary.csv`
- `original_challenge_signal_family_results.csv`
- `original_challenge_cost_sensitivity.csv`

Regenerate these tables with:

```bash
python -m src.build_reports
```
