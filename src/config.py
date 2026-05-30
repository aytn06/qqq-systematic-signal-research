from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class BacktestConfig:
  train_start: str = "2000-01-01"
  train_end: str = "2015-12-31"
  valid_start: str = "2016-01-01"
  valid_end: str = "2021-12-31"
  holdout_start: str = "2022-01-01"
  holdout_end: str = "2025-06-30"

  min_exposure: float = -1.0
  max_exposure: float = 1.5
  trading_days: int = 252

  # One-way transaction cost per unit turnover.
  # 0.0005 = 5 bps.
  transaction_cost: float = 0.0005


def infer_backtest_config(index) -> BacktestConfig:
  """
  Choose a reasonable split configuration for the available history.

  The bundled included sample uses a shorter 2018-2025 range than the
  original challenge protocol, so the CLI defaults should adapt rather than
  reporting an empty training window.
  """
  dates = pd.Index(index).unique().sort_values()
  start = dates.min()
  end = dates.max()

  canonical_public_sample = (
    start <= pd.Timestamp("2018-01-02")
    and end >= pd.Timestamp("2025-06-30")
  )
  if canonical_public_sample:
    return BacktestConfig(
      train_start="2018-01-01",
      train_end="2020-12-31",
      valid_start="2021-01-01",
      valid_end="2022-12-31",
      holdout_start="2023-01-01",
      holdout_end="2025-06-30",
      transaction_cost=0.0005,
    )

  train_end = dates[int(len(dates) * 0.45)]
  valid_end = dates[int(len(dates) * 0.70)]
  return BacktestConfig(
    train_start=str(dates[0].date()),
    train_end=str(train_end.date()),
    valid_start=str((train_end + pd.Timedelta(days=1)).date()),
    valid_end=str(valid_end.date()),
    holdout_start=str((valid_end + pd.Timedelta(days=1)).date()),
    holdout_end=str(dates[-1].date()),
    transaction_cost=0.0005,
  )
