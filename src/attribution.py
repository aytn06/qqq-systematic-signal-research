from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd

from .backtest import compute_strategy_returns
from .config import BacktestConfig
from .metrics import summarize_backtest


def component_contribution_timeseries(
    returns: pd.Series,
    signals: pd.DataFrame,
    selected_signals: list[str],
    config: BacktestConfig,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not selected_signals:
        empty = pd.DataFrame(index=signals.index)
        return empty, empty

    component_exposures = signals[selected_signals].div(len(selected_signals))
    applied_exposures = component_exposures.shift(1).fillna(0.0)
    gross_contrib = applied_exposures.mul(returns, axis=0)

    ensemble_exposure = component_exposures.sum(axis=1)
    ensemble_turnover = ensemble_exposure.diff().abs().fillna(ensemble_exposure.abs())
    component_turnover = component_exposures.diff().abs().fillna(component_exposures.abs())
    total_component_turnover = component_turnover.sum(axis=1).replace(0.0, np.nan)
    component_cost = component_turnover.div(total_component_turnover, axis=0).mul(
        config.transaction_cost * ensemble_turnover,
        axis=0,
    )
    component_cost = component_cost.fillna(0.0)
    net_contrib = gross_contrib - component_cost
    return net_contrib, component_exposures


def _split_windows(config: BacktestConfig) -> dict[str, tuple[str | None, str | None]]:
    return {
        "train": (config.train_start, config.train_end),
        "validation": (config.valid_start, config.valid_end),
        "holdout": (config.holdout_start, config.holdout_end),
        "full": (None, None),
    }


def summarize_component_attribution(
    returns: pd.Series,
    signals: pd.DataFrame,
    selected_signals: list[str],
    config: BacktestConfig,
) -> pd.DataFrame:
    contrib, component_exposures = component_contribution_timeseries(returns, signals, selected_signals, config)
    if contrib.empty:
        return pd.DataFrame()

    ensemble_exposure = component_exposures.sum(axis=1).rename("final_research_ensemble")
    ensemble_bt = compute_strategy_returns(returns, ensemble_exposure, config=config, shift_exposure=True)
    rows: list[dict[str, object]] = []
    for split, (start, end) in _split_windows(config).items():
        if start is None or end is None:
            split_contrib = contrib
            split_exposure = component_exposures
            split_bt = ensemble_bt
        else:
            split_contrib = contrib.loc[start:end]
            split_exposure = component_exposures.loc[start:end]
            split_bt = ensemble_bt.loc[start:end]

        for signal in selected_signals:
            signal_returns = split_contrib[signal]
            metrics = summarize_backtest(
                pd.DataFrame(
                    {
                        "net_return": signal_returns,
                        "turnover": split_exposure[signal].diff().abs().fillna(split_exposure[signal].abs()),
                        "cost": 0.0,
                        "exposure": split_exposure[signal],
                    }
                ),
                config=config,
                return_col="net_return",
            )
            rows.append(
                {
                    "signal": signal,
                    "split": split,
                    "total_return": metrics["total_return"],
                    "ann_return": metrics["ann_return"],
                    "ann_vol": metrics["ann_vol"],
                    "sharpe": metrics["sharpe"],
                    "max_drawdown": metrics["max_drawdown"],
                    "avg_abs_component_exposure": split_exposure[signal].abs().mean(),
                    "correlation_to_ensemble": signal_returns.corr(split_bt["net_return"]),
                    "positive_day_share": (signal_returns > 0).mean(),
                }
            )
    return pd.DataFrame(rows)


def exposure_state_summary(exposures: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for name, series in exposures.items():
        valid = series.dropna()
        if valid.empty:
            continue
        rows.append(
            {
                "series": name,
                "avg_exposure": valid.mean(),
                "avg_abs_exposure": valid.abs().mean(),
                "short_share": (valid < 0.0).mean(),
                "flat_share": (valid == 0.0).mean(),
                "long_share": ((valid > 0.0) & (valid <= 1.0)).mean(),
                "levered_long_share": (valid > 1.0).mean(),
            }
        )
    return pd.DataFrame(rows)
