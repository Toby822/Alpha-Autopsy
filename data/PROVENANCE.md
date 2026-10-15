# Market data provenance

Alpha Autopsy's historical-price observations are not synthetic.

**Source as accessed:** [SubhayanBiswas / Binance-Vision-Sample-Data](https://github.com/SubhayanBiswas/Binance-Vision-Sample-Data/blob/main/BTCUSDT_1h_Cleaned.csv). The repository describes its upstream as [Binance public USD-M Futures historical klines](https://data.binance.vision/?prefix=data/futures/um/monthly/klines/BTCUSDT/1h/). This is a **third-party historical mirror**, not a direct live exchange feed. The source repository says the hourly records cover January 2024 through December 2025. The Binance public-data documentation notes that source timestamps differ by vintage; this mirror uses human-readable dates.

**Pinned upstream Git blob SHA-1:** `629859ca96ea5e13816c10ce74bdd48e01ba93dd`

**Bundled dataset:** `btcusdt_2024_2025_daily_close.csv`

- Input: 17,544 hourly OHLCV records, CSV columns `Date, Open, High, Low, Close, Volume`.
- Transformation: take the **close of the 23:00 UTC hourly candle each day**, retaining original quoted USDT prices to one decimal place. This approximates a 24-hour daily close, not the next day opening price.
- Output: 731 daily close observations between 2024-01-01 and 2025-12-31 inclusive.
- First price: 44,230.2 USDT. Last price: 87,608.2 USDT.
- Integrity: strict chronological dates, no missing daily dates and checks on expected date range/length. The rebuild tool also checks the original Git blob hash and rejects a changed source unless explicitly overridden.
- Currency: BTC/USDT, rather than BTC/USD. USDT is not USD cash.

To re-create the price snapshot from source (requires internet):

```bash
python scripts/rebuild_data.py
python -m src.research
```

The report and downloaded source have not been independently audited against exchange executions, and the mirror's presence on GitHub should not be read as permission to republish or redistribute its entire dataset. The repository contains a small derived daily-close series with this attribution. Review the original provider's terms before other downstream redistribution or commercial reuse.