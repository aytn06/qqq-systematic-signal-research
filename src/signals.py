"""Signal definitions for daily QQQ exposure allocation."""

from __future__ import annotations

import pandas as pd

from .features import sma, ema, rsi, parkinson_vol, atr, rolling_skew, month_turn_indicator


SIGNAL_FAMILY_MAP = {
  "long_term_trend": "trend",
  "medium_term_trend": "trend",
  "rsi_deep_value": "volatility_mean_reversion",
  "rsi_gated_short": "defensive_volatility",
  "conservative_fade": "defensive_volatility",
  "vol_shock_dampener": "risk_control",
  "skew_filter": "risk_control",
  "dual_trend_macro": "cross_asset_macro",
  "turn_of_month": "seasonality",
}


def clip_exposure(signal: pd.Series, min_exposure: float = -1.0, max_exposure: float = 1.5) -> pd.Series:
  return signal.clip(lower=min_exposure, upper=max_exposure)


def long_term_trend(df: pd.DataFrame, window: int = 200) -> pd.Series:
  """Long 1.5x above long-term trend, cash otherwise."""
  exp = pd.Series(0.0, index=df.index)
  exp[df["qqq_close"] > sma(df["qqq_close"], window)] = 1.5
  return exp.rename("long_term_trend")


def medium_term_trend(df: pd.DataFrame, window: int = 50) -> pd.Series:
  """Tactical trend exposure based on medium-term moving average."""
  exp = pd.Series(0.0, index=df.index)
  exp[df["qqq_close"] > ema(df["qqq_close"], window)] = 1.25
  exp[df["qqq_close"] < ema(df["qqq_close"], window)] = -0.25
  return exp.rename("medium_term_trend")


def rsi_deep_value(
  df: pd.DataFrame,
  vol_window: int = 21,
  rsi_window: int = 14,
  low_vol: float = 0.15,
  high_vol: float = 0.30,
  extreme_vol: float = 0.50,
  oversold: float = 20,
) -> pd.Series:
  """
  Volatility-regime model that aggressively buys deeply oversold selloffs.

  Intuition:
  - Low realized volatility: risk-on, high exposure.
  - High volatility: defensive / short.
  - Extreme oversold: override to long, attempting to avoid selling the hole.
  """
  vol = parkinson_vol(df["qqq_high"], df["qqq_low"], window=vol_window)
  r = rsi(df["qqq_close"], window=rsi_window)

  exp = pd.Series(0.5, index=df.index)
  exp[vol <= low_vol] = 1.5
  exp[(vol > low_vol) & (vol <= high_vol)] = 1.0
  exp[(vol > high_vol) & (vol <= extreme_vol)] = -0.5
  exp[vol > extreme_vol] = 0.0
  exp[r < oversold] = 1.5
  return exp.rename("rsi_deep_value")


def rsi_gated_short(
  df: pd.DataFrame,
  vol_window: int = 21,
  rsi_window: int = 14,
  low_vol: float = 0.15,
  high_vol: float = 0.30,
  oversold: float = 30,
) -> pd.Series:
  """
  Defensive volatility-regime model that avoids shorting when QQQ is already oversold.
  """
  vol = parkinson_vol(df["qqq_high"], df["qqq_low"], window=vol_window)
  r = rsi(df["qqq_close"], window=rsi_window)

  exp = pd.Series(0.5, index=df.index)
  exp[vol <= low_vol] = 1.5
  exp[(vol > low_vol) & (vol <= high_vol)] = 1.0
  exp[vol > high_vol] = -0.5
  exp[(vol > high_vol) & (r < oversold)] = 0.0
  return exp.rename("rsi_gated_short")


def conservative_fade(
  df: pd.DataFrame,
  vol_window: int = 21,
  low_vol: float = 0.15,
  high_vol: float = 0.30,
  extreme_vol: float = 0.50,
) -> pd.Series:
  """
  Volatility-regime model that goes to cash during extreme volatility.
  """
  vol = parkinson_vol(df["qqq_high"], df["qqq_low"], window=vol_window)

  exp = pd.Series(0.5, index=df.index)
  exp[vol <= low_vol] = 1.5
  exp[(vol > low_vol) & (vol <= high_vol)] = 1.0
  exp[(vol > high_vol) & (vol <= extreme_vol)] = -0.5
  exp[vol > extreme_vol] = 0.0
  return exp.rename("conservative_fade")


def vol_shock_dampener(
  df: pd.DataFrame,
  atr_window: int = 14,
  shock_multiple: float = 2.0,
) -> pd.Series:
  """
  Cuts exposure after unusually large true-range shocks.
  """
  base = long_term_trend(df, window=200).fillna(0.0)
  current_tr = (df["qqq_high"] - df["qqq_low"]).abs()
  avg_tr = atr(df["qqq_high"], df["qqq_low"], df["qqq_close"], window=atr_window)
  shock = current_tr > shock_multiple * avg_tr

  exp = base.copy()
  exp[shock] = 0.5 * exp[shock]
  return exp.rename("vol_shock_dampener")


def skew_filter(
  df: pd.DataFrame,
  vol_window: int = 21,
  skew_window: int = 21,
  high_vol: float = 0.30,
  positive_skew: float = 0.5,
) -> pd.Series:
  """
  Avoids shorting during high-volatility periods with positive return skew,
  which may indicate violent bear-market rallies.
  """
  exp = conservative_fade(df, vol_window=vol_window)
  vol = parkinson_vol(df["qqq_high"], df["qqq_low"], window=vol_window)
  skew = rolling_skew(df["qqq_return"], window=skew_window)
  exp[(vol > high_vol) & (skew > positive_skew)] = 0.0
  return exp.rename("skew_filter")


def dual_trend_macro(
  df: pd.DataFrame,
  qqq_window: int = 200,
  dxy_window: int = 200,
) -> pd.Series:
  """
  Cross-asset regime signal combining QQQ trend and DXY trend.

  Example logic:
  - QQQ above trend and DXY below trend: risk-on, 1.5x long.
  - QQQ below trend and DXY above trend: risk-off, short.
  - Otherwise: neutral/cash.
  """
  qqq_up = df["qqq_close"] > sma(df["qqq_close"], qqq_window)
  dxy_up = df["dxy_close"] > sma(df["dxy_close"], dxy_window)

  exp = pd.Series(0.0, index=df.index)
  exp[qqq_up & (~dxy_up)] = 1.5
  exp[qqq_up & dxy_up] = 0.75
  exp[(~qqq_up) & dxy_up] = -0.5
  exp[(~qqq_up) & (~dxy_up)] = 0.25
  return exp.rename("dual_trend_macro")


def turn_of_month(df: pd.DataFrame, before: int = 1, after: int = 3) -> pd.Series:
  ind = month_turn_indicator(df.index, before=before, after=after)
  exp = pd.Series(0.5, index=df.index)
  exp[ind == 1] = 1.5
  return exp.rename("turn_of_month")


SIGNAL_FUNCTIONS = {
  "long_term_trend": long_term_trend,
  "medium_term_trend": medium_term_trend,
  "rsi_deep_value": rsi_deep_value,
  "rsi_gated_short": rsi_gated_short,
  "conservative_fade": conservative_fade,
  "vol_shock_dampener": vol_shock_dampener,
  "skew_filter": skew_filter,
  "dual_trend_macro": dual_trend_macro,
  "turn_of_month": turn_of_month,
}


SIGNAL_DEFAULT_PARAMS = {
  "long_term_trend": {"window": 200},
  "medium_term_trend": {"window": 50},
  "rsi_deep_value": {
    "vol_window": 21,
    "rsi_window": 14,
    "low_vol": 0.15,
    "high_vol": 0.30,
    "extreme_vol": 0.50,
    "oversold": 20.0,
  },
  "rsi_gated_short": {
    "vol_window": 21,
    "rsi_window": 14,
    "low_vol": 0.15,
    "high_vol": 0.30,
    "oversold": 30.0,
  },
  "conservative_fade": {
    "vol_window": 21,
    "low_vol": 0.15,
    "high_vol": 0.30,
    "extreme_vol": 0.50,
  },
  "vol_shock_dampener": {
    "atr_window": 14,
    "shock_multiple": 2.0,
  },
  "skew_filter": {
    "vol_window": 21,
    "skew_window": 21,
    "high_vol": 0.30,
    "positive_skew": 0.5,
  },
  "dual_trend_macro": {
    "qqq_window": 200,
    "dxy_window": 200,
  },
  "turn_of_month": {
    "before": 1,
    "after": 3,
  },
}


def build_signal_matrix(df: pd.DataFrame) -> pd.DataFrame:
  """Compute the default signal set."""
  signal_fns = [
    long_term_trend,
    medium_term_trend,
    rsi_deep_value,
    rsi_gated_short,
    conservative_fade,
    vol_shock_dampener,
    skew_filter,
    dual_trend_macro,
    turn_of_month,
  ]
  signals = [fn(df) for fn in signal_fns]
  return pd.concat(signals, axis=1)


def equal_weight_ensemble(signals: pd.DataFrame, min_exposure: float = -1.0, max_exposure: float = 1.5) -> pd.Series:
  """Simple baseline ensemble: average signals and clip to allowed exposure range."""
  exp = signals.mean(axis=1)
  return clip_exposure(exp, min_exposure=min_exposure, max_exposure=max_exposure).rename("equal_weight_ensemble")
