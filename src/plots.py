from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .metrics import equity_curve


def plot_equity_curves(strategy_returns: dict[str, pd.Series], output_path: str) -> None:
    plt.figure(figsize=(10, 6))
    for name, returns in strategy_returns.items():
        curve = equity_curve(returns)
        plt.plot(curve.index, curve.values, label=name)
    plt.title("Equity Curves")
    plt.xlabel("Date")
    plt.ylabel("Growth of $1")
    plt.legend()
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_drawdown(returns: pd.Series, output_path: str, title: str = "Drawdown") -> None:
    curve = equity_curve(returns)
    dd = curve / curve.cummax() - 1
    plt.figure(figsize=(10, 4))
    plt.plot(dd.index, dd.values)
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_signal_correlation(signals: pd.DataFrame, output_path: str) -> None:
    corr = signals.dropna().corr()
    plt.figure(figsize=(8, 6))
    plt.imshow(corr, aspect="auto")
    plt.colorbar(label="Correlation")
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.index)), corr.index)
    plt.title("Signal Exposure Correlation")
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
