from __future__ import annotations

import numpy as np
import pandas as pd

from .config import BacktestConfig
from .metrics import annualized_return, max_drawdown, sharpe_ratio


def moving_block_bootstrap(
    returns: pd.Series,
    block_size: int = 20,
    n_boot: int = 400,
    seed: int = 7,
) -> pd.DataFrame:
    series = returns.dropna()
    if series.empty:
        return pd.DataFrame(columns=["sample"])

    values = series.to_numpy()
    n = len(values)
    rng = np.random.default_rng(seed)
    draws = np.empty((n_boot, n))
    for i in range(n_boot):
        pieces = []
        while sum(len(piece) for piece in pieces) < n:
            start = int(rng.integers(0, max(n - block_size + 1, 1)))
            stop = min(start + block_size, n)
            pieces.append(values[start:stop])
        draws[i] = np.concatenate(pieces)[:n]
    return pd.DataFrame(draws)


def bootstrap_metric_summary(
    returns: pd.Series,
    config: BacktestConfig,
    block_size: int = 20,
    n_boot: int = 400,
    seed: int = 7,
) -> pd.DataFrame:
    boot = moving_block_bootstrap(returns, block_size=block_size, n_boot=n_boot, seed=seed)
    if boot.empty:
        return pd.DataFrame()

    sharpe_samples = boot.apply(lambda row: sharpe_ratio(pd.Series(row), config.trading_days), axis=1)
    ann_return_samples = boot.apply(lambda row: annualized_return(pd.Series(row), config.trading_days), axis=1)
    drawdown_samples = boot.apply(lambda row: max_drawdown(pd.Series(row)), axis=1)

    point = pd.Series(
        {
            "sharpe": sharpe_ratio(returns, config.trading_days),
            "ann_return": annualized_return(returns, config.trading_days),
            "max_drawdown": max_drawdown(returns),
        }
    )
    samples = {
        "sharpe": sharpe_samples,
        "ann_return": ann_return_samples,
        "max_drawdown": drawdown_samples,
    }
    rows = []
    for metric, sample in samples.items():
        sample = sample.dropna()
        rows.append(
            {
                "metric": metric,
                "point_estimate": point[metric],
                "bootstrap_median": sample.median(),
                "bootstrap_p10": sample.quantile(0.10),
                "bootstrap_p25": sample.quantile(0.25),
                "bootstrap_p75": sample.quantile(0.75),
                "bootstrap_p90": sample.quantile(0.90),
                "probability_positive": (sample > 0).mean() if metric != "max_drawdown" else (sample > -0.10).mean(),
                "n_boot": len(sample),
                "block_size": block_size,
            }
        )
    return pd.DataFrame(rows)
