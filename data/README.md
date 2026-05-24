# Data

This repo ships with one sanitized public file, `sample_prices.csv`, so the QQQ
pipeline can run end to end without any private market data.

The minimum schema is:

```text
date,qqq_close,qqq_high,qqq_low,dxy_close
```

Optional future columns:

```text
qqq_volume,spy_close,vix_close,tlt_close,rates_10y
```

The committed sample is not the original Quanta challenge dataset. It exists so
the signal code, backtest, plots, and summary-generation scripts can be run
publicly.

If you swap in your own research data locally, keep the same column names and
date structure.
