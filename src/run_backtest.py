from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .config import BacktestConfig
from .data_loader import load_price_data, add_returns
from .signals import build_signal_matrix, equal_weight_ensemble
from .backtest import backtest_many
from .metrics import summarize_by_split


DEFAULT_INPUT = "data/sample_prices.csv"
DEFAULT_OUTPUT = "results/performance_summary.csv"


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        description="Run the baseline QQQ signal backtest suite and write a split-by-split summary.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )


def main() -> None:
    parser = build_parser()
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Path to CSV data.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Path to output performance summary CSV.")
    args = parser.parse_args()

    config = BacktestConfig()
    df = add_returns(load_price_data(args.input))

    signals = build_signal_matrix(df)
    ensemble = equal_weight_ensemble(signals, config.min_exposure, config.max_exposure)
    buy_and_hold = pd.Series(1.0, index=df.index, name="buy_and_hold")
    exposures = pd.concat([buy_and_hold, signals, ensemble], axis=1)

    backtests = backtest_many(df["qqq_return"], exposures, config=config, shift_exposure=True)
    summary = summarize_by_split(backtests, config=config, return_col="net_return")
    summary["split"] = pd.Categorical(
        summary["split"],
        categories=["train", "validation", "holdout", "full"],
        ordered=True,
    )
    summary = summary.sort_values(["split", "sharpe", "strategy"], ascending=[True, False, True]).reset_index(drop=True)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output, index=False)

    empty_splits = summary.groupby("split", observed=True)["ann_return"].apply(lambda col: col.isna().all())
    missing = [split for split, is_empty in empty_splits.items() if is_empty]
    if missing:
        print(f"Note: no rows were available for split(s): {', '.join(missing)}")

    cols = ["strategy", "split", "ann_return", "ann_vol", "sharpe", "max_drawdown", "avg_turnover"]
    print(summary[cols].to_string(index=False))


if __name__ == "__main__":
    main()
