from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd

from .config import BacktestConfig
from .data_loader import load_price_data, add_returns
from .signals import build_signal_matrix, equal_weight_ensemble
from .backtest import backtest_many

DEFAULT_INPUT = "data/sample_prices.csv"
DEFAULT_OUTPUT_DIR = "figures"


def ensure_matplotlib_cache_dir() -> None:
    """
    Use a repo-local Matplotlib config directory when the caller has not
    explicitly provided one. This avoids cache writes into unwritable home
    locations in sandboxed or CI environments.
    """
    if "MPLCONFIGDIR" not in os.environ:
        cache_dir = Path(".mplconfig").resolve()
        cache_dir.mkdir(parents=True, exist_ok=True)
        os.environ["MPLCONFIGDIR"] = str(cache_dir)
    os.environ.setdefault("MPLBACKEND", "Agg")


ensure_matplotlib_cache_dir()

from .plots import plot_equity_curves, plot_drawdown, plot_signal_correlation


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        description="Generate standard diagnostic plots for the baseline QQQ research pipeline.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )


def main() -> None:
    parser = build_parser()
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Path to CSV data.")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Directory for plots.")
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
