from pathlib import Path

import pytest

from src.data_loader import load_price_data


def test_load_price_data_rejects_missing_columns(tmp_path: Path) -> None:
    path = tmp_path / "missing_columns.csv"
    path.write_text("date,qqq_close\n2020-01-01,10\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required columns"):
        load_price_data(str(path))


def test_load_price_data_sorts_and_deduplicates_dates(tmp_path: Path) -> None:
    path = tmp_path / "prices.csv"
    path.write_text(
        "\n".join(
            [
                "date,qqq_close,qqq_high,qqq_low,dxy_close",
                "2020-01-03,11,12,10,99",
                "2020-01-01,10,11,9,100",
                "2020-01-01,10,11,9,100",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    df = load_price_data(str(path))

    assert list(df.index.strftime("%Y-%m-%d")) == ["2020-01-01", "2020-01-03"]
    assert list(df.columns) == ["qqq_close", "qqq_high", "qqq_low", "dxy_close"]
