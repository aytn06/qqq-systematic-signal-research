# Results

Committed result tables in this repo:

- `final_performance_summary.csv`: headline benchmark, selected sleeves, and final ensemble comparison
- `model_selection_summary.csv`: validation-only family ranking and final public-ensemble membership
- `signal_family_results.csv`: family representative table including validation and holdout context
- `cost_sensitivity.csv`: holdout metrics across one-way cost assumptions
- `parameter_sensitivity.csv`: +/- 10% parameter perturbation results for the selected sleeves
- `regime_summary.csv`: structural and event-window regime breakdowns
- `public_data_split.csv`: exact train / validation / holdout dates for the public sample
- `original_challenge_performance_summary.csv`: preserved summary-statistic table for the private-run challenge result
- `original_challenge_signal_family_results.csv`: original challenge family-level summary table
- `original_challenge_cost_sensitivity.csv`: original challenge cost-sensitivity summary table
- `performance_summary.csv`: baseline backtest-suite output from `src.run_backtest`

Regenerate the public artifact pack with:

```bash
python -m src.generate_research_artifacts
```
