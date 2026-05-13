from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .config import BacktestConfig
from .data_loader import load_price_data, add_returns
from .signals import build_signal_matrix, equal_weight_ensemble
from .backtest import backtest_many
from .plots import plot_equity_curves, plot_drawdown, plot_signal_correlation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to CSV data.")
    parser.add_argument("--output-dir", required=True, help="Directory for plots.")
    args = parser.parse_args()

    config = BacktestConfig()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = add_returns(load_price_data(args.input))
    signals = build_signal_matrix(df)
    ensemble = equal_weight_ensemble(signals, config.min_exposure, config.max_exposure)
    exposures = pd.concat([signals, ensemble], axis=1)
    backtests = backtest_many(df["qqq_return"], exposures, config=config, shift_exposure=True)

    selected = {
        "buy_and_hold": df["qqq_return"],
        "equal_weight_ensemble": backtests["equal_weight_ensemble"]["net_return"],
        "rsi_deep_value": backtests["rsi_deep_value"]["net_return"],
        "dual_trend_macro": backtests["dual_trend_macro"]["net_return"],
    }

    plot_equity_curves(selected, str(output_dir / "equity_curves.png"))
    plot_drawdown(backtests["equal_weight_ensemble"]["net_return"], str(output_dir / "ensemble_drawdown.png"))
    plot_signal_correlation(signals, str(output_dir / "signal_correlation.png"))

    print(f"Wrote plots to {output_dir}")


if __name__ == "__main__":
    main()
