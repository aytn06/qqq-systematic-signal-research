from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .config import BacktestConfig
from .data_loader import load_price_data, add_returns
from .signals import build_signal_matrix, equal_weight_ensemble
from .backtest import backtest_many
from .metrics import summarize_by_split


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to CSV data.")
    parser.add_argument("--output", required=True, help="Path to output performance summary CSV.")
    args = parser.parse_args()

    config = BacktestConfig()
    df = add_returns(load_price_data(args.input))

    signals = build_signal_matrix(df)
    ensemble = equal_weight_ensemble(signals, config.min_exposure, config.max_exposure)
    exposures = pd.concat([signals, ensemble], axis=1)

    backtests = backtest_many(df["qqq_return"], exposures, config=config, shift_exposure=True)
    summary = summarize_by_split(backtests, config=config, return_col="net_return")

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output, index=False)

    cols = ["strategy", "split", "ann_return", "ann_vol", "sharpe", "max_drawdown", "avg_turnover"]
    print(summary[cols].to_string(index=False))


if __name__ == "__main__":
    main()
