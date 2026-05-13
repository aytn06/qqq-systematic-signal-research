import pandas as pd

from src.backtest import compute_strategy_returns
from src.config import BacktestConfig
from src.metrics import summarize_backtest, summarize_by_split


def make_backtest_fixture() -> tuple[pd.DataFrame, BacktestConfig]:
    index = pd.date_range("2020-01-01", periods=9, freq="D")
    returns = pd.Series([0.01, -0.005, 0.002, 0.003, -0.002, 0.004, 0.001, -0.003, 0.002], index=index)
    exposure = pd.Series(1.0, index=index)
    config = BacktestConfig(
        train_start="2020-01-01",
        train_end="2020-01-03",
        valid_start="2020-01-04",
        valid_end="2020-01-06",
        holdout_start="2020-01-07",
        holdout_end="2020-01-09",
    )
    return compute_strategy_returns(returns, exposure, config=config, shift_exposure=True), config


def test_summarize_backtest_returns_expected_fields() -> None:
    bt, config = make_backtest_fixture()

    summary = summarize_backtest(bt, config)

    expected = {
        "ann_return",
        "ann_vol",
        "sharpe",
        "max_drawdown",
        "calmar",
        "avg_turnover",
        "cost_drag_ann",
        "avg_exposure",
    }
    assert expected.issubset(summary.keys())
    assert summary["ann_vol"] >= 0


def test_summarize_by_split_includes_all_splits() -> None:
    bt, config = make_backtest_fixture()

    summary = summarize_by_split({"demo": bt}, config)

    assert set(summary["split"]) == {"train", "validation", "holdout", "full"}
    assert set(summary["strategy"]) == {"demo"}
