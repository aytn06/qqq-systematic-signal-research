from pathlib import Path

from src.config import BacktestConfig
from src.data_loader import load_price_data, add_returns
from src.signals import build_signal_matrix, equal_weight_ensemble
from src.backtest import compute_strategy_returns

SAMPLE_DATA = Path(__file__).resolve().parents[1] / "data" / "sample_prices.csv"


def test_pipeline_runs_on_sample_data():
    df = add_returns(load_price_data(str(SAMPLE_DATA)))
    signals = build_signal_matrix(df)
    assert not signals.empty
    assert "rsi_deep_value" in signals.columns

    config = BacktestConfig()
    ensemble = equal_weight_ensemble(signals, config.min_exposure, config.max_exposure)
    bt = compute_strategy_returns(df["qqq_return"], ensemble, config=config, shift_exposure=True)

    assert {"gross_return", "net_return", "turnover", "cost"}.issubset(bt.columns)
    assert bt["exposure"].max() <= config.max_exposure
    assert bt["exposure"].min() >= config.min_exposure


def test_exposure_is_shifted():
    df = add_returns(load_price_data(str(SAMPLE_DATA)))
    config = BacktestConfig()
    signals = build_signal_matrix(df)
    exposure = equal_weight_ensemble(signals, config.min_exposure, config.max_exposure)
    bt = compute_strategy_returns(df["qqq_return"], exposure, config=config, shift_exposure=True)
    assert bt["applied_exposure"].iloc[0] == 0.0
