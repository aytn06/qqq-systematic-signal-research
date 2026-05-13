from __future__ import annotations

import copy
from typing import Callable, Any

import pandas as pd

from .config import BacktestConfig
from .backtest import compute_strategy_returns
from .metrics import summarize_backtest


def perturb_numeric_params(params: dict[str, Any], pct: float = 0.10) -> list[dict[str, Any]]:
    """
    Produce parameter dictionaries where each numeric parameter is moved down/up by pct.

    Integer parameters are rounded and constrained to be at least 1.
    """
    variants = []
    for key, value in params.items():
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            for mult in [1 - pct, 1 + pct]:
                new_params = copy.deepcopy(params)
                new_params[key] = max(1, int(round(value * mult)))
                variants.append(new_params)
        elif isinstance(value, float):
            for mult in [1 - pct, 1 + pct]:
                new_params = copy.deepcopy(params)
                new_params[key] = value * mult
                variants.append(new_params)
    return variants


def sensitivity_analysis(
    df: pd.DataFrame,
    returns: pd.Series,
    signal_fn: Callable[..., pd.Series],
    base_params: dict[str, Any],
    config: BacktestConfig,
    pct: float = 0.10,
) -> pd.DataFrame:
    """
    Run ±pct parameter sensitivity for a signal function.
    """
    rows = []

    all_params = [base_params] + perturb_numeric_params(base_params, pct=pct)
    labels = ["base"] + [f"variant_{i}" for i in range(1, len(all_params))]

    for label, params in zip(labels, all_params):
        exposure = signal_fn(df, **params)
        bt = compute_strategy_returns(returns, exposure, config=config, shift_exposure=True)

        for split, split_bt in {
            "train": bt.loc[config.train_start : config.train_end],
            "validation": bt.loc[config.valid_start : config.valid_end],
            "holdout": bt.loc[config.holdout_start : config.holdout_end],
        }.items():
            row = summarize_backtest(split_bt, config)
            row["signal"] = signal_fn.__name__
            row["variant"] = label
            row["split"] = split
            row["params"] = str(params)
            rows.append(row)

    return pd.DataFrame(rows)


def no_lookahead_smoke_test(exposure: pd.Series, returns: pd.Series) -> bool:
    """
    Minimal smoke test: exposure index must align with returns.
    This does not prove absence of lookahead; it catches common implementation mistakes.
    """
    return exposure.index.equals(returns.index)
