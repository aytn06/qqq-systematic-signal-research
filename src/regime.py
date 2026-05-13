from __future__ import annotations

import pandas as pd

from .features import sma, parkinson_vol
from .metrics import summarize_backtest
from .config import BacktestConfig


def classify_regimes(df: pd.DataFrame) -> pd.Series:
    """
    Simple interpretable regime classifier.

    Regimes:
    - bull_low_vol
    - bull_high_vol
    - bear_low_vol
    - bear_high_vol
    """
    trend = df["qqq_close"] > sma(df["qqq_close"], 200)
    vol = parkinson_vol(df["qqq_high"], df["qqq_low"], 21)
    high_vol = vol > vol.rolling(252, min_periods=60).median()

    regime = pd.Series("unknown", index=df.index)
    regime[trend & ~high_vol] = "bull_low_vol"
    regime[trend & high_vol] = "bull_high_vol"
    regime[~trend & ~high_vol] = "bear_low_vol"
    regime[~trend & high_vol] = "bear_high_vol"
    return regime


def regime_summary(bt: pd.DataFrame, regimes: pd.Series, config: BacktestConfig) -> pd.DataFrame:
    rows = []
    aligned = bt.join(regimes.rename("regime"), how="left")
    for regime, sub in aligned.groupby("regime"):
        row = summarize_backtest(sub, config)
        row["regime"] = regime
        rows.append(row)
    return pd.DataFrame(rows)
