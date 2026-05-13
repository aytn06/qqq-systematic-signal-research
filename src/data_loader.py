from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = {"date", "qqq_close", "qqq_high", "qqq_low", "dxy_close"}


def load_price_data(path: str) -> pd.DataFrame:
    """Load and validate daily price data."""
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").drop_duplicates("date").set_index("date")
    df = df.astype(float)
    return df


def add_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Add close-to-close percentage returns."""
    out = df.copy()
    out["qqq_return"] = out["qqq_close"].pct_change()
    out["dxy_return"] = out["dxy_close"].pct_change()
    return out.dropna()
