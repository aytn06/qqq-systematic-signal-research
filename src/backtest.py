from __future__ import annotations

import pandas as pd

from .config import BacktestConfig


def compute_strategy_returns(
    returns: pd.Series,
    exposure: pd.Series,
    config: BacktestConfig,
    shift_exposure: bool = True,
) -> pd.DataFrame:
    """
    Convert an exposure series into gross and net strategy returns.

    If shift_exposure=True, exposure decided at time t is applied to the next
    return. This conservative choice avoids accidental look-ahead bias.
    """
    exp = exposure.reindex(returns.index).fillna(0.0)

    applied_exp = exp.shift(1).fillna(0.0) if shift_exposure else exp
    gross = applied_exp * returns

    turnover = exp.diff().abs().fillna(exp.abs())
    cost = config.transaction_cost * turnover
    net = gross - cost

    return pd.DataFrame(
        {
            "exposure": exp,
            "applied_exposure": applied_exp,
            "gross_return": gross,
            "turnover": turnover,
            "cost": cost,
            "net_return": net,
        },
        index=returns.index,
    )


def split_returns(bt: pd.DataFrame, config: BacktestConfig) -> dict[str, pd.DataFrame]:
    """Return train/validation/holdout slices."""
    return {
        "train": bt.loc[config.train_start : config.train_end],
        "validation": bt.loc[config.valid_start : config.valid_end],
        "holdout": bt.loc[config.holdout_start : config.holdout_end],
    }


def backtest_many(
    returns: pd.Series,
    exposures: pd.DataFrame,
    config: BacktestConfig,
    shift_exposure: bool = True,
) -> dict[str, pd.DataFrame]:
    out = {}
    for name in exposures.columns:
        out[name] = compute_strategy_returns(
            returns=returns,
            exposure=exposures[name],
            config=config,
            shift_exposure=shift_exposure,
        )
    return out
