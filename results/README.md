# Results

This folder holds the public result tables generated from the committed sample
dataset.

Main files:

- `final_performance_summary.csv`: the benchmark, representative sleeves, and
  final ensemble comparison
- `model_selection_summary.csv`: validation-only ranking and final public
  ensemble membership
- `signal_family_results.csv`: family-level representative table
- `cost_sensitivity.csv`: holdout performance under different one-way cost
  assumptions
- `parameter_sensitivity.csv`: +/- 10% parameter perturbations for the selected
  sleeves
- `regime_summary.csv`: structural and event-window regime breakdowns
- `public_data_split.csv`: exact train / validation / holdout dates used for
  the public sample

The folder also keeps summary files for the original private challenge run:

- `original_challenge_performance_summary.csv`
- `original_challenge_signal_family_results.csv`
- `original_challenge_cost_sensitivity.csv`

Regenerate the public tables with:

```bash
python -m src.generate_research_artifacts
```
