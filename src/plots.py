from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

if "MPLCONFIGDIR" not in os.environ:
    cache_dir = Path(".mplconfig").resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ["MPLCONFIGDIR"] = str(cache_dir)
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt

from .metrics import equity_curve, rolling_sharpe


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
    plot_correlation_heatmap(corr, output_path, title="Signal Exposure Correlation")


def plot_correlation_heatmap(corr: pd.DataFrame, output_path: str, title: str) -> None:
    plt.figure(figsize=(8, 6))
    plt.imshow(corr, aspect="auto")
    plt.colorbar(label="Correlation")
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.index)), corr.index)
    plt.title(title)
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_drawdown_comparison(strategy_returns: dict[str, pd.Series], output_path: str, title: str = "Drawdown Comparison") -> None:
    plt.figure(figsize=(10, 4))
    for name, returns in strategy_returns.items():
        curve = equity_curve(returns)
        dd = curve / curve.cummax() - 1
        plt.plot(dd.index, dd.values, label=name)
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.legend()
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_rolling_sharpe(strategy_returns: dict[str, pd.Series], output_path: str, window: int = 126, trading_days: int = 252) -> None:
    plt.figure(figsize=(10, 4))
    for name, returns in strategy_returns.items():
        series = rolling_sharpe(returns, window=window, trading_days=trading_days)
        plt.plot(series.index, series.values, label=name)
    plt.axhline(0.0, color="black", linewidth=0.8, linestyle="--")
    plt.title(f"Rolling {window}-Day Sharpe")
    plt.xlabel("Date")
    plt.ylabel("Sharpe")
    plt.legend()
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_cost_sensitivity(cost_df: pd.DataFrame, output_path: str, split: str = "holdout", metric: str = "sharpe") -> None:
    subset = cost_df[cost_df["split"] == split].copy()
    plt.figure(figsize=(10, 5))
    for strategy, group in subset.groupby("display_name"):
        ordered = group.sort_values("cost_bps")
        plt.plot(ordered["cost_bps"], ordered[metric], marker="o", label=strategy)
    plt.title(f"Cost Sensitivity ({split.title()} {metric.replace('_', ' ').title()})")
    plt.xlabel("Transaction Cost (bps)")
    plt.ylabel(metric.replace("_", " ").title())
    plt.legend()
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_parameter_sensitivity_heatmap(
    sensitivity_df: pd.DataFrame,
    output_path: str,
    split: str = "holdout",
    metric: str = "sharpe",
) -> None:
    subset = sensitivity_df[sensitivity_df["split"] == split].copy()
    pivot = subset.pivot(index="signal", columns="variant", values=metric).fillna(np.nan)
    plt.figure(figsize=(11, 4 + 0.5 * len(pivot.index)))
    im = plt.imshow(pivot.values, aspect="auto")
    plt.colorbar(im, label=metric.replace("_", " ").title())
    plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=45, ha="right")
    plt.yticks(range(len(pivot.index)), pivot.index)
    for row_idx, row in enumerate(pivot.values):
        for col_idx, value in enumerate(row):
            if not np.isnan(value):
                plt.text(col_idx, row_idx, f"{value:.2f}", ha="center", va="center", fontsize=8)
    plt.title(f"Parameter Sensitivity ({split.title()} {metric.replace('_', ' ').title()})")
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_regime_breakdown(
    regime_df: pd.DataFrame,
    output_path: str,
    metric: str = "ann_return",
    regime_set: str = "structural",
    strategies: list[str] | None = None,
) -> None:
    subset = regime_df[regime_df["regime_set"] == regime_set].copy()
    if strategies is not None:
        subset = subset[subset["strategy"].isin(strategies)]
    pivot = subset.pivot(index="regime", columns="display_name", values=metric).fillna(0.0)
    ax = pivot.plot(kind="bar", figsize=(10, 5))
    ax.set_title(f"Regime Breakdown ({regime_set.replace('_', ' ').title()})")
    ax.set_xlabel("Regime")
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.legend(title="")
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_component_contribution_curves(contribution_df: pd.DataFrame, output_path: str) -> None:
    plt.figure(figsize=(10, 5))
    for signal in contribution_df.columns:
        curve = (1 + contribution_df[signal].fillna(0.0)).cumprod()
        plt.plot(curve.index, curve.values, label=signal)
    plt.title("Selected Signal Contribution Curves")
    plt.xlabel("Date")
    plt.ylabel("Growth of $1")
    plt.legend()
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_walkforward_holdout(performance_df: pd.DataFrame, output_path: str) -> None:
    if performance_df.empty:
        return
    plt.figure(figsize=(10, 4.5))
    folds = performance_df["fold"]
    x = np.arange(len(folds))
    width = 0.35
    plt.bar(x - width / 2, performance_df["validation_sharpe"], width=width, label="Validation Sharpe")
    plt.bar(x + width / 2, performance_df["holdout_sharpe"], width=width, label="Holdout Sharpe")
    plt.axhline(0.0, color="black", linewidth=0.8, linestyle="--")
    plt.xticks(x, folds)
    plt.ylabel("Sharpe")
    plt.xlabel("Walk-forward fold")
    plt.title("Walk-Forward Ensemble Selection")
    plt.legend()
    plt.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
