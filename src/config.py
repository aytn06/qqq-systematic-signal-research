from dataclasses import dataclass


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
