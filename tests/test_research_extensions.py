from pathlib import Path

from src.attribution import component_contribution_timeseries, exposure_state_summary, summarize_component_attribution
from src.backtest import backtest_many
from src.config import infer_backtest_config
from src.data_loader import add_returns, load_price_data
from src.signals import build_signal_matrix
from src.walkforward import build_walkforward_windows, evaluate_walkforward_selection


SAMPLE_DATA = Path(__file__).resolve().parents[1] / "data" / "sample_prices.csv"


def test_walkforward_selection_runs_on_sample_data():
    df = add_returns(load_price_data(str(SAMPLE_DATA)))
    config = infer_backtest_config(df.index)
    signals = build_signal_matrix(df)
    signal_backtests = backtest_many(df["qqq_return"], signals, config=config, shift_exposure=True)

    performance, selection = evaluate_walkforward_selection(
        returns=df["qqq_return"],
        signals=signals,
        signal_backtests=signal_backtests,
        config=config,
        min_train=252,
        validation=126,
        holdout=63,
        step=63,
    )

    assert not performance.empty
    assert {"fold", "selected_signals", "holdout_sharpe"}.issubset(performance.columns)
    assert not selection.empty


def test_component_attribution_sums_to_selected_signal_frame():
    df = add_returns(load_price_data(str(SAMPLE_DATA)))
    config = infer_backtest_config(df.index)
    signals = build_signal_matrix(df)
    selected = ["medium_term_trend", "rsi_deep_value", "turn_of_month"]

    contributions, component_exposures = component_contribution_timeseries(
        returns=df["qqq_return"],
        signals=signals,
        selected_signals=selected,
        config=config,
    )

    assert list(contributions.columns) == selected
    assert component_exposures.shape[1] == len(selected)

    summary = summarize_component_attribution(
        returns=df["qqq_return"],
        signals=signals,
        selected_signals=selected,
        config=config,
    )
    states = exposure_state_summary(component_exposures.sum(axis=1).rename("ensemble").to_frame())

    assert {"signal", "split", "sharpe"}.issubset(summary.columns)
    assert {"series", "short_share", "long_share"}.issubset(states.columns)
