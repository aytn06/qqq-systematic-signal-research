from __future__ import annotations

import copy
from typing import Callable, Any

import pandas as pd

from .config import BacktestConfig
from .backtest import compute_strategy_returns
from .metrics import summarize_backtest


def build_parameter_variants(params: dict[str, Any], pct: float = 0.10) -> list[dict[str, Any]]:
    """Produce labeled parameter variants moved down/up by pct."""
    variants = [
        {
            "variant": "base",
            "params": copy.deepcopy(params),
            "changed_param": "base",
            "direction": "base",
            "change_pct": 0.0,
        }
    ]
    for key, value in params.items():
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            for direction, mult in [("down", 1 - pct), ("up", 1 + pct)]:
                new_params = copy.deepcopy(params)
                new_params[key] = max(1, int(round(value * mult)))
                variants.append(
                    {
                        "variant": f"{key}_{direction}",
                        "params": new_params,
                        "changed_param": key,
                        "direction": direction,
                        "change_pct": -pct if direction == "down" else pct,
                    }
                )
        elif isinstance(value, float):
            for direction, mult in [("down", 1 - pct), ("up", 1 + pct)]:
                new_params = copy.deepcopy(params)
                new_params[key] = value * mult
                variants.append(
                    {
                        "variant": f"{key}_{direction}",
                        "params": new_params,
                        "changed_param": key,
                        "direction": direction,
                        "change_pct": -pct if direction == "down" else pct,
                    }
                )
    return variants


def perturb_numeric_params(params: dict[str, Any], pct: float = 0.10) -> list[dict[str, Any]]:
    """
    Backward-compatible helper that returns parameter dictionaries only.
    """
    return [variant["params"] for variant in build_parameter_variants(params, pct=pct)][1:]


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

    for variant in build_parameter_variants(base_params, pct=pct):
        params = variant["params"]
        exposure = signal_fn(df, **params)
        bt = compute_strategy_returns(returns, exposure, config=config, shift_exposure=True)

        for split, split_bt in {
            "train": bt.loc[config.train_start : config.train_end],
            "validation": bt.loc[config.valid_start : config.valid_end],
            "holdout": bt.loc[config.holdout_start : config.holdout_end],
        }.items():
            row = summarize_backtest(split_bt, config)
            row["signal"] = signal_fn.__name__
            row["variant"] = variant["variant"]
            row["changed_param"] = variant["changed_param"]
            row["direction"] = variant["direction"]
            row["change_pct"] = variant["change_pct"]
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
