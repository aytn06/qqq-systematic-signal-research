# Data

This repo ships with one included file, `sample_prices.csv`, so the QQQ
pipeline can run end to end without reposting challenge-provided market data.

The minimum schema is:

```text
date,qqq_close,qqq_high,qqq_low,dxy_close
```

Optional future columns:

```text
qqq_volume,spy_close,vix_close,tlt_close,rates_10y
```

The committed sample is not the original Quanta challenge dataset. The original
finalist submission used data provided through the Quanta QR Fellowship
challenge, and that source dataset is not redistributable here. This included
file exists so the signal code, backtest, plots, and summary-generation
scripts can still run end to end in the repo.

I imported this repo dataset and the supporting summaries later from my private
research archive, which is why some git timestamps are newer than the original
project dates.

If you swap in your own research data locally, keep the same column names and
date structure.
