from __future__ import annotations

from dataclasses import replace

import pandas as pd

from .backtest import compute_strategy_returns
from .config import BacktestConfig
from .metrics import summarize_backtest, summarize_by_split
from .signals import SIGNAL_FAMILY_MAP, clip_exposure


def build_walkforward_windows(
    index: pd.Index,
    min_train: int = 504,
    validation: int = 252,
    holdout: int = 126,
    step: int = 126,
) -> list[dict[str, object]]:
    dates = pd.Index(index).unique().sort_values()
    windows: list[dict[str, object]] = []
    fold = 1
    train_end_idx = min_train - 1
    while train_end_idx + validation + holdout < len(dates):
        valid_start_idx = train_end_idx + 1
        valid_end_idx = valid_start_idx + validation - 1
        holdout_start_idx = valid_end_idx + 1
        holdout_end_idx = holdout_start_idx + holdout - 1
        windows.append(
            {
                "fold": f"fold_{fold}",
                "train_start": str(dates[0].date()),
                "train_end": str(dates[train_end_idx].date()),
                "valid_start": str(dates[valid_start_idx].date()),
                "valid_end": str(dates[valid_end_idx].date()),
                "holdout_start": str(dates[holdout_start_idx].date()),
                "holdout_end": str(dates[holdout_end_idx].date()),
            }
        )
        train_end_idx += step
        fold += 1
    return windows


def _fold_config(base: BacktestConfig, window: dict[str, object]) -> BacktestConfig:
    return replace(
        base,
        train_start=window["train_start"],
        train_end=window["train_end"],
        valid_start=window["valid_start"],
        valid_end=window["valid_end"],
        holdout_start=window["holdout_start"],
        holdout_end=window["holdout_end"],
    )


def _validation_selection_score(candidates: pd.DataFrame) -> pd.Series:
    return (
        candidates["validation_sharpe"].fillna(-10.0)
        + 0.50 * candidates["validation_max_drawdown"].fillna(-1.0)
        - 0.25 * candidates["validation_avg_turnover"].fillna(0.0)
        - 0.10 * candidates["validation_cost_drag_ann"].fillna(0.0)
    )


def _select_signals_for_fold(signals: pd.DataFrame, signal_summary: pd.DataFrame, config: BacktestConfig) -> tuple[list[str], pd.DataFrame]:
    validation = signal_summary[signal_summary["split"] == "validation"].copy()
    validation = validation.rename(columns={c: f"validation_{c}" for c in validation.columns if c not in {"strategy", "split"}})
    candidates = (
        pd.DataFrame({"signal": list(signals.columns)})
        .assign(family=lambda df_: df_["signal"].map(SIGNAL_FAMILY_MAP))
        .merge(validation.drop(columns=["split"]), left_on="signal", right_on="strategy", how="left")
        .drop(columns=["strategy"])
    )
    candidates["score"] = _validation_selection_score(candidates)

    validation_slice = signals.loc[config.valid_start : config.valid_end]
    corr = validation_slice.corr().abs().fillna(0.0)

    family_best = (
        candidates.sort_values(["score", "validation_sharpe", "validation_max_drawdown"], ascending=[False, False, False])
        .groupby("family", as_index=False)
        .head(1)
        .reset_index(drop=True)
    )

    selected: list[str] = []
    rows: list[dict[str, object]] = []
    for _, row in family_best.sort_values(["score", "validation_sharpe"], ascending=[False, False]).iterrows():
        signal = row["signal"]
        max_corr = max((corr.loc[signal, chosen] for chosen in selected), default=0.0)
        keep = pd.notna(row["validation_sharpe"]) and row["validation_sharpe"] > 0 and max_corr <= 0.80
        if keep:
            selected.append(signal)
        rows.append(
            {
                "signal": signal,
                "family": row["family"],
                "selected": keep,
                "validation_score": row["score"],
                "validation_sharpe": row["validation_sharpe"],
                "max_abs_validation_corr_to_selected": max_corr,
                "selection_reason": "kept" if keep else "rejected",
            }
        )

    return selected, pd.DataFrame(rows)


def evaluate_walkforward_selection(
    returns: pd.Series,
    signals: pd.DataFrame,
    signal_backtests: dict[str, pd.DataFrame],
    config: BacktestConfig,
    min_train: int = 504,
    validation: int = 252,
    holdout: int = 126,
    step: int = 126,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    windows = build_walkforward_windows(
        signals.index,
        min_train=min_train,
        validation=validation,
        holdout=holdout,
        step=step,
    )
    performance_rows: list[dict[str, object]] = []
    selection_rows: list[dict[str, object]] = []

    for window in windows:
        fold_config = _fold_config(config, window)
        fold_summary = summarize_by_split(signal_backtests, config=fold_config, return_col="net_return")
        selected, selection_df = _select_signals_for_fold(signals, fold_summary, fold_config)
        if selected:
            final_exposure = clip_exposure(
                signals[selected].mean(axis=1),
                min_exposure=config.min_exposure,
                max_exposure=config.max_exposure,
            )
        else:
            final_exposure = pd.Series(0.0, index=signals.index, name="flat_if_no_signal")
        final_bt = compute_strategy_returns(returns, final_exposure, config=fold_config, shift_exposure=True)
        validation_metrics = summarize_backtest(final_bt.loc[fold_config.valid_start : fold_config.valid_end], fold_config)
        holdout_metrics = summarize_backtest(final_bt.loc[fold_config.holdout_start : fold_config.holdout_end], fold_config)
        performance_rows.append(
            {
                **window,
                "selected_signals": ", ".join(selected),
                "n_selected": len(selected),
                "flat_if_empty": len(selected) == 0,
                "validation_sharpe": validation_metrics["sharpe"],
                "holdout_sharpe": holdout_metrics["sharpe"],
                "holdout_ann_return": holdout_metrics["ann_return"],
                "holdout_max_drawdown": holdout_metrics["max_drawdown"],
                "holdout_avg_turnover": holdout_metrics["avg_turnover"],
            }
        )
        if not selection_df.empty:
            selection_df = selection_df.assign(fold=window["fold"])
            selection_rows.append(selection_df)

    performance = pd.DataFrame(performance_rows)
    selections = pd.concat(selection_rows, ignore_index=True) if selection_rows else pd.DataFrame()
    return performance, selections
