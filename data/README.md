# Data

Do not commit large raw market-data files or data you do not have permission to redistribute.

Expected schema:

```text
date, qqq_close, qqq_high, qqq_low, dxy_close
```

Optional columns:

```text
qqq_volume, spy_close, vix_close, tlt_close, rates_10y
```

The included `sample_prices.csv` is synthetic and exists only to test that the pipeline runs.
Replace it with your actual research data locally.
