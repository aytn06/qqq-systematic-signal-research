from __future__ import annotations

import numpy as np
import pandas as pd


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=window).mean()


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False, min_periods=span).mean()


def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """Wilder-style RSI."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr


def atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    return true_range(high, low, close).rolling(window=window, min_periods=window).mean()


def parkinson_vol(high: pd.Series, low: pd.Series, window: int = 21, annualize: bool = True) -> pd.Series:
    """
    Parkinson volatility estimator based on high-low ranges.

    Uses only same-day high/low information. In the backtest, final exposures
    are shifted by one day before being applied to returns.
    """
    const = 1.0 / (4.0 * np.log(2.0))
    hl = np.log(high / low) ** 2
    var = const * hl.rolling(window=window, min_periods=window).mean()
    vol = np.sqrt(var)
    if annualize:
        vol = vol * np.sqrt(252)
    return vol


def rolling_skew(returns: pd.Series, window: int = 21) -> pd.Series:
    return returns.rolling(window=window, min_periods=window).skew()


def month_turn_indicator(index: pd.DatetimeIndex, before: int = 1, after: int = 3) -> pd.Series:
    """
    Indicator for days around the turn of the month.

    before=1 includes the last business day of the month.
    after=3 includes the first three business days of the month.
    """
    df = pd.DataFrame(index=index)
    df["month"] = index.to_period("M")
    df["rank_in_month"] = df.groupby("month").cumcount() + 1
    df["rev_rank_in_month"] = df.iloc[::-1].groupby("month").cumcount().iloc[::-1] + 1
    ind = ((df["rev_rank_in_month"] <= before) | (df["rank_in_month"] <= after)).astype(float)
    return ind
