from __future__ import annotations

import argparse
import os
from dataclasses import replace
from pathlib import Path

import pandas as pd

from .backtest import backtest_many
from .attribution import (
    component_contribution_timeseries,
    exposure_state_summary,
    summarize_component_attribution,
)
from .config import BacktestConfig, infer_backtest_config
from .data_loader import add_returns, load_price_data
from .inference import bootstrap_metric_summary
from .metrics import summarize_by_split
from .plots import (
    plot_component_contribution_curves,
    plot_correlation_heatmap,
    plot_cost_sensitivity,
    plot_drawdown_comparison,
    plot_equity_curves,
    plot_parameter_sensitivity_heatmap,
    plot_regime_breakdown,
    plot_rolling_sharpe,
    plot_walkforward_holdout,
)
from .regime import classify_regimes, regime_summary
from .signals import (
    SIGNAL_DEFAULT_PARAMS,
    SIGNAL_FAMILY_MAP,
    SIGNAL_FUNCTIONS,
    build_signal_matrix,
    clip_exposure,
)
from .validation import sensitivity_analysis
from .walkforward import evaluate_walkforward_selection


DEFAULT_INPUT = "data/sample_prices.csv"
DEFAULT_RESULTS_DIR = "results"
DEFAULT_FIGURES_DIR = "figures"
DEFAULT_COST_GRID_BPS = [1, 5, 10, 20]

DISPLAY_NAMES = {
    "buy_and_hold": "Buy & Hold QQQ",
    "long_term_trend": "Long-Term Trend",
    "medium_term_trend": "Medium-Term Trend",
    "rsi_deep_value": "RSI Deep Value",
    "rsi_gated_short": "RSI Gated Short",
    "conservative_fade": "Conservative Fade",
    "vol_shock_dampener": "Vol Shock Dampener",
    "skew_filter": "Skew Filter",
    "dual_trend_macro": "Dual Trend Macro",
    "turn_of_month": "Turn of Month",
    "equal_weight_ensemble": "Equal-Weight Signal Zoo",
    "final_research_ensemble": "Final Research Ensemble",
}


def ensure_matplotlib_cache_dir() -> None:
    if "MPLCONFIGDIR" not in os.environ:
        cache_dir = Path(".mplconfig").resolve()
        cache_dir.mkdir(parents=True, exist_ok=True)
        os.environ["MPLCONFIGDIR"] = str(cache_dir)
    os.environ.setdefault("MPLBACKEND", "Agg")


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        description="Build the committed result tables and figures for the QQQ signal project.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )


def signal_split_metrics(summary: pd.DataFrame, split: str) -> pd.DataFrame:
    subset = summary[summary["split"] == split].copy()
    return subset.rename(
        columns={
            "strategy": "signal",
            "ann_return": f"{split}_ann_return",
            "ann_vol": f"{split}_ann_vol",
            "sharpe": f"{split}_sharpe",
            "max_drawdown": f"{split}_max_drawdown",
            "calmar": f"{split}_calmar",
            "avg_turnover": f"{split}_avg_turnover",
            "cost_drag_ann": f"{split}_cost_drag_ann",
            "avg_exposure": f"{split}_avg_exposure",
            "total_return": f"{split}_total_return",
        }
    ).drop(columns=["split"])


def validation_selection_score(candidates: pd.DataFrame) -> pd.Series:
    """
    Build a validation-only ranking score for family representatives.

    Higher validation Sharpe is better. Less-negative drawdown is rewarded,
    while turnover and annualized cost drag are lightly penalized.
    """
    return (
        candidates["validation_sharpe"].fillna(-10.0)
        + 0.50 * candidates["validation_max_drawdown"].fillna(-1.0)
        - 0.25 * candidates["validation_avg_turnover"].fillna(0.0)
        - 0.10 * candidates["validation_cost_drag_ann"].fillna(0.0)
    )


def select_validation_signals(
    signals: pd.DataFrame,
    signal_backtests: dict[str, pd.DataFrame],
    config: BacktestConfig,
) -> tuple[list[str], pd.DataFrame]:
    summary = summarize_by_split(signal_backtests, config=config, return_col="net_return")
    validation = signal_split_metrics(summary, "validation")
    holdout = signal_split_metrics(summary, "holdout")
    full = signal_split_metrics(summary, "full")

    candidates = (
        pd.DataFrame({"signal": list(signals.columns)})
        .assign(family=lambda df_: df_["signal"].map(SIGNAL_FAMILY_MAP))
        .merge(validation, on="signal", how="left")
        .merge(holdout, on="signal", how="left")
        .merge(full, on="signal", how="left")
    )
    candidates["validation_selection_score"] = validation_selection_score(candidates)

    validation_slice = signals.loc[config.valid_start : config.valid_end]
    corr = validation_slice.corr().abs().fillna(0.0)

    family_best = (
        candidates.sort_values(
            [
                "validation_selection_score",
                "validation_sharpe",
                "validation_max_drawdown",
                "validation_avg_turnover",
            ],
            ascending=[False, False, False, True],
        )
        .groupby("family", as_index=False)
        .head(1)
        .reset_index(drop=True)
    )

    selected: list[str] = []
    selection_rows = []
    max_selected = 4
    for _, row in family_best.sort_values(
        [
            "validation_selection_score",
            "validation_sharpe",
            "validation_max_drawdown",
            "validation_avg_turnover",
        ],
        ascending=[False, False, False, True],
    ).iterrows():
        signal = row["signal"]
        max_corr = max((corr.loc[signal, chosen] for chosen in selected), default=0.0)
        min_abs_diff = min(
            (
                (validation_slice[signal] - validation_slice[chosen]).abs().mean()
                for chosen in selected
            ),
            default=pd.NA,
        )
        duplicate_profile = pd.notna(min_abs_diff) and min_abs_diff < 0.05
        positive_validation = pd.notna(row["validation_sharpe"]) and row["validation_sharpe"] > 0
        keep = (
            len(selected) < max_selected
            and positive_validation
            and not duplicate_profile
            and (max_corr <= 0.80 or len(selected) == 0)
        )
        if keep:
            selected.append(signal)
        selection_rows.append(
            {
                "signal": signal,
                "family": row["family"],
                "selected_for_final_ensemble": keep,
                "selection_order": len(selected) if keep else pd.NA,
                "max_abs_validation_corr_to_selected": max_corr,
                "min_mean_abs_exposure_diff_to_selected": min_abs_diff,
                "duplicate_validation_profile": duplicate_profile,
                "positive_validation": positive_validation,
            }
        )

    selection = family_best.merge(pd.DataFrame(selection_rows), on=["signal", "family"], how="left")

    selection["display_name"] = selection["signal"].map(DISPLAY_NAMES)
    selection["selection_policy"] = "keep only positive-validation, non-duplicate, low-correlation representatives"
    selection["flat_ensemble_if_empty"] = len(selected) == 0
    return selected, selection.sort_values(
        ["selected_for_final_ensemble", "validation_selection_score", "validation_sharpe"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def structural_and_event_regimes(df: pd.DataFrame) -> pd.DataFrame:
    structural = pd.DataFrame(
        {
            "regime_set": "structural",
            "regime": classify_regimes(df),
        },
        index=df.index,
    )

    event = pd.Series("all_other_periods", index=df.index, name="regime")
    event.loc["2020-02-15":"2020-08-31"] = "2020_crash_rebound"
    event.loc["2022-01-01":"2022-12-31"] = "2022_bear_market"
    event.loc["2023-01-01":"2024-12-31"] = "2023_2024_recovery"
    event_frame = pd.DataFrame({"regime_set": "event_window", "regime": event}, index=df.index)

    return pd.concat([structural, event_frame])


def save_public_split(config: BacktestConfig, output_path: Path) -> None:
    split_df = pd.DataFrame(
        [
            {"split": "train", "start": config.train_start, "end": config.train_end},
            {"split": "validation", "start": config.valid_start, "end": config.valid_end},
            {"split": "holdout", "start": config.holdout_start, "end": config.holdout_end},
        ]
    )
    split_df.to_csv(output_path, index=False)


def main() -> None:
    ensure_matplotlib_cache_dir()

    parser = build_parser()
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Path to the public data CSV.")
    parser.add_argument("--results-dir", default=DEFAULT_RESULTS_DIR, help="Directory for generated CSV results.")
    parser.add_argument("--figures-dir", default=DEFAULT_FIGURES_DIR, help="Directory for generated figures.")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    figures_dir = Path(args.figures_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    df = add_returns(load_price_data(args.input))
    config = infer_backtest_config(df.index)

    signals = build_signal_matrix(df)
    signal_backtests = backtest_many(df["qqq_return"], signals, config=config, shift_exposure=True)
    selected_signals, selection = select_validation_signals(signals, signal_backtests, config)

    buy_and_hold = pd.Series(1.0, index=df.index, name="buy_and_hold")
    equal_weight = clip_exposure(signals.mean(axis=1), min_exposure=config.min_exposure, max_exposure=config.max_exposure).rename("equal_weight_ensemble")
    if selected_signals:
        final_ensemble = clip_exposure(
            signals[selected_signals].mean(axis=1),
            min_exposure=config.min_exposure,
            max_exposure=config.max_exposure,
        ).rename("final_research_ensemble")
    else:
        final_ensemble = pd.Series(0.0, index=df.index, name="final_research_ensemble")

    exposures = pd.concat([buy_and_hold, signals, equal_weight, final_ensemble], axis=1)
    backtests = backtest_many(df["qqq_return"], exposures, config=config, shift_exposure=True)
    summary = summarize_by_split(backtests, config=config, return_col="net_return")
    summary["display_name"] = summary["strategy"].map(DISPLAY_NAMES).fillna(summary["strategy"])

    selection.to_csv(results_dir / "signal_family_results.csv", index=False)
    selection.loc[:, [
        "family",
        "signal",
        "display_name",
        "selected_for_final_ensemble",
        "selection_order",
        "validation_selection_score",
        "validation_sharpe",
        "validation_max_drawdown",
        "validation_avg_turnover",
        "validation_cost_drag_ann",
        "holdout_sharpe",
        "max_abs_validation_corr_to_selected",
    ]].to_csv(
        results_dir / "model_selection_summary.csv",
        index=False,
    )

    representative_rows = []
    trend_signal = selection[selection["family"] == "trend"].iloc[0]["signal"]
    vol_signal = selection[selection["family"] == "volatility_mean_reversion"].iloc[0]["signal"]
    report_strategies = [
        "buy_and_hold",
        trend_signal,
        vol_signal,
        "dual_trend_macro",
        "final_research_ensemble",
    ]
    for strategy in report_strategies:
        subset = summary[summary["strategy"] == strategy].copy()
        metrics_by_split = subset.set_index("split")
        representative_rows.append(
            {
                "strategy": strategy,
                "display_name": DISPLAY_NAMES.get(strategy, strategy),
                "validation_sharpe": metrics_by_split.get("sharpe", pd.Series()).get("validation", pd.NA),
                "holdout_sharpe": metrics_by_split.get("sharpe", pd.Series()).get("holdout", pd.NA),
                "validation_total_return": metrics_by_split.get("total_return", pd.Series()).get("validation", pd.NA),
                "holdout_total_return": metrics_by_split.get("total_return", pd.Series()).get("holdout", pd.NA),
                "holdout_max_drawdown": metrics_by_split.get("max_drawdown", pd.Series()).get("holdout", pd.NA),
                "holdout_ann_vol": metrics_by_split.get("ann_vol", pd.Series()).get("holdout", pd.NA),
                "holdout_turnover": metrics_by_split.get("avg_turnover", pd.Series()).get("holdout", pd.NA),
                "cost_assumption_bps": int(config.transaction_cost * 10000),
            }
        )
    pd.DataFrame(representative_rows).to_csv(results_dir / "final_performance_summary.csv", index=False)

    cost_rows = []
    for cost_bps in DEFAULT_COST_GRID_BPS:
        cost_config = replace(config, transaction_cost=cost_bps / 10000.0)
        cost_backtests = backtest_many(df["qqq_return"], exposures[report_strategies], config=cost_config, shift_exposure=True)
        cost_summary = summarize_by_split(cost_backtests, config=cost_config, return_col="net_return")
        cost_summary["cost_bps"] = cost_bps
        cost_summary["display_name"] = cost_summary["strategy"].map(DISPLAY_NAMES).fillna(cost_summary["strategy"])
        cost_rows.append(cost_summary)
    cost_df = pd.concat(cost_rows, ignore_index=True)
    cost_df.to_csv(results_dir / "cost_sensitivity.csv", index=False)

    sensitivity_frames = []
    for signal in selected_signals:
        base_params = SIGNAL_DEFAULT_PARAMS[signal]
        sensitivity_frames.append(
            sensitivity_analysis(
                df=df,
                returns=df["qqq_return"],
                signal_fn=SIGNAL_FUNCTIONS[signal],
                base_params=base_params,
                config=config,
                pct=0.10,
            ).assign(family=SIGNAL_FAMILY_MAP[signal], display_name=DISPLAY_NAMES.get(signal, signal))
        )
    sensitivity_df = pd.concat(sensitivity_frames, ignore_index=True) if sensitivity_frames else pd.DataFrame()
    sensitivity_df.to_csv(results_dir / "parameter_sensitivity.csv", index=False)

    bootstrap_rows = []
    for strategy in ["buy_and_hold", *selected_signals, "final_research_ensemble"]:
        bt = backtests[strategy].loc[config.holdout_start : config.holdout_end]
        stats = bootstrap_metric_summary(bt["net_return"], config=config, block_size=20, n_boot=400, seed=7)
        if stats.empty:
            continue
        stats["strategy"] = strategy
        stats["display_name"] = DISPLAY_NAMES.get(strategy, strategy)
        stats["split"] = "holdout"
        bootstrap_rows.append(stats)
    bootstrap_df = pd.concat(bootstrap_rows, ignore_index=True) if bootstrap_rows else pd.DataFrame()
    bootstrap_df.to_csv(results_dir / "holdout_bootstrap_summary.csv", index=False)

    regime_rows = []
    regime_sets = structural_and_event_regimes(df)
    for regime_set, regime_frame in regime_sets.groupby("regime_set"):
        regime_series = regime_frame["regime"]
        for strategy in ["buy_and_hold", "final_research_ensemble", *selected_signals]:
            summary_frame = regime_summary(backtests[strategy], regime_series, config).assign(
                strategy=strategy,
                display_name=DISPLAY_NAMES.get(strategy, strategy),
                regime_set=regime_set,
            )
            regime_rows.append(summary_frame)
    regime_df = pd.concat(regime_rows, ignore_index=True)
    regime_df.to_csv(results_dir / "regime_summary.csv", index=False)

    contribution_df, component_exposures = component_contribution_timeseries(
        returns=df["qqq_return"],
        signals=signals,
        selected_signals=selected_signals,
        config=config,
    )
    contribution_df.to_csv(results_dir / "ensemble_component_contributions.csv", index_label="date")
    component_exposures.to_csv(results_dir / "selected_signal_component_exposures.csv", index_label="date")
    summarize_component_attribution(
        returns=df["qqq_return"],
        signals=signals,
        selected_signals=selected_signals,
        config=config,
    ).to_csv(results_dir / "component_attribution_summary.csv", index=False)
    exposure_state_summary(
        pd.concat(
            [
                signals[selected_signals],
                final_ensemble.rename("final_research_ensemble"),
            ],
            axis=1,
        )
    ).to_csv(results_dir / "exposure_state_summary.csv", index=False)

    walkforward_performance, walkforward_selection = evaluate_walkforward_selection(
        returns=df["qqq_return"],
        signals=signals,
        signal_backtests=signal_backtests,
        config=config,
    )
    walkforward_performance.to_csv(results_dir / "walkforward_performance.csv", index=False)
    walkforward_selection.to_csv(results_dir / "walkforward_selection.csv", index=False)

    selected_signal_returns = {
        DISPLAY_NAMES.get(signal, signal): backtests[signal]["net_return"] for signal in selected_signals
    }
    plot_equity_curves(
        {
            DISPLAY_NAMES["buy_and_hold"]: backtests["buy_and_hold"]["net_return"],
            DISPLAY_NAMES["final_research_ensemble"]: backtests["final_research_ensemble"]["net_return"],
            **selected_signal_returns,
        },
        str(figures_dir / "final_equity_curve.png"),
    )
    plot_drawdown_comparison(
        {
            DISPLAY_NAMES["buy_and_hold"]: backtests["buy_and_hold"]["net_return"],
            DISPLAY_NAMES["final_research_ensemble"]: backtests["final_research_ensemble"]["net_return"],
        },
        str(figures_dir / "final_drawdown.png"),
    )
    plot_rolling_sharpe(
        {
            DISPLAY_NAMES["buy_and_hold"]: backtests["buy_and_hold"]["net_return"],
            DISPLAY_NAMES["final_research_ensemble"]: backtests["final_research_ensemble"]["net_return"],
        },
        str(figures_dir / "rolling_sharpe.png"),
        trading_days=config.trading_days,
    )
    if selected_signals:
        plot_correlation_heatmap(
            signals[selected_signals].corr(),
            str(figures_dir / "signal_correlation_heatmap.png"),
            title="Selected Signal Correlation",
        )
    plot_cost_sensitivity(cost_df, str(figures_dir / "cost_sensitivity.png"))
    if not sensitivity_df.empty:
        plot_parameter_sensitivity_heatmap(
            sensitivity_df,
            str(figures_dir / "parameter_sensitivity_heatmap.png"),
        )
    plot_regime_breakdown(
        regime_df,
        str(figures_dir / "regime_breakdown.png"),
        strategies=["buy_and_hold", "final_research_ensemble"],
    )
    plot_component_contribution_curves(
        contribution_df,
        str(figures_dir / "component_contributions.png"),
    )
    plot_walkforward_holdout(
        walkforward_performance,
        str(figures_dir / "walkforward_selection.png"),
    )

    save_public_split(config, results_dir / "public_data_split.csv")

    print(f"Wrote results and figures to {results_dir} and {figures_dir}")


if __name__ == "__main__":
    main()
