# Alpha Autopsy

**A trading signal is easy to find. A signal that survives is harder.**

Alpha Autopsy is a small, reproducible research study into selection bias in systematic trading. It begins with a deliberately modest idea: choose the best of ten momentum and reversal rules using one year's data, and then see what happens when that choice faces a new year.

It isn't an algorithm that predicts the market. The interesting result is that the rule selected in the training period **doesn't hold up in forward evaluation**.

### [Open the interactive research dashboard](https://toby822.github.io/Alpha-Autopsy/)

## The experiment, in numbers

| | What was fixed beforehand | What happened |
|---|---|---:|
| Candidate universe | Momentum and reversal × 2, 5, 10, 20, 40 days | 10 rules |
| Training window | 1 Jan – 31 Dec 2024 | Selected **2-day momentum** |
| Training Sharpe | Winner chosen only from 2024 | **+0.51** |
| Validation | Jan – Jun 2025 | **−1.68** Sharpe |
| Untouched test | Jul – Dec 2025 | **−0.06** Sharpe |
| Holdout net return | With 10 bps per position unit traded | **−4.2%** |
| Alignment placebo | Circular shifts within the test set | **0.321** diagnostic one-sided probability |

Those are **historical backtest estimates**, not actual executed returns. The Sharpe ratios are annualised using 365 crypto-market days. The sample is too short to draw strong general conclusions, and the placebo is not a formal proof of signal significance.

The narrower finding is useful: a simple training-only optimisation produced a rule that looked modestly promising in 2024 but was not robust in the following periods. That's precisely the sort of false confidence a careful quant research process should try to catch.

## What the app lets you investigate

- **Frozen experiment:** inspect the 2-day momentum rule that was selected using the training period only.
- **All trials, not just the winner:** explore all ten candidate signals in one comparison table and a train-versus-holdout scatter plot.
- **Trading friction:** vary a fixed fee-plus-slippage proxy from 0–40 basis points per unit of position turnover. A direct short-to-long flip costs twice as much as entering from flat.
- **Forward-performance plot:** chart training, validation and test segments, with a simple buy-and-hold price-return reference.
- **Placebo and uncertainty:** inspect a circular-shift signal-alignment diagnostic and a moving-block bootstrap confidence interval for mean daily return.
- **Export and audit:** export the currently selected experiment settings and all metrics to JSON.

The interactive controls are **exploratory**. If you use the test results to choose another rule or fee assumption, that new choice no longer qualifies as a pre-selected holdout experiment. The app displays this distinction explicitly.

## Reproduce the research

Requirements: Python 3.11+ with NumPy and pandas; Node.js 18+ for JavaScript parity tests. No API key needed. All historical prices used in the displayed analysis are bundled, so the main study runs offline.

```bash
python -m pip install -r requirements.txt
python -m src.research
python -m unittest discover -s tests -v
node tests/test_engine.cjs
```

To open the web app locally:

```bash
python -m http.server 8000
```

Open **http://localhost:8000**. Opening `index.html` directly as a local file won't load its JSON research artifact in most browsers.

Optional browser smoke test (Playwright + Chromium required):

```bash
python -m pip install playwright
python -m playwright install chromium
python tests/browser_smoke.py
```

## How the timing works

Signals are calculated only from prices available **at the preceding day's close**. The resulting position is applied to the next close-to-close price return. Every position change incurs the assumed cost. Position is restricted to −1, 0, or +1.

```
signal at t−1  →  position for (t−1,t]  →  observed price return at t
```

The Python model produces `research/results.json`; the browser implementation independently recalculates metrics from those same raw prices and checks its output against the Python report. If you are new to quantitative finance, start with [the plain-English explanation](docs/START_HERE.md). See [the research methods](research/METHODS.md) for formulas and [the findings](research/FINDINGS.md) for interpretation.

## What is and isn't real

The **price observations are historical**, not generated. They are daily snapshots (23:00 UTC hourly candle close) from a third-party mirror which identifies its upstream as Binance BTC/USDT USD-M futures. We did not independently verify every observation with the exchange. The price data, timeframe, the original Git blob hash and a rebuild script are documented in [data provenance](data/PROVENANCE.md).

The **trading executions are hypothetical**. There is no exchange order book, filled orders, leverage/funding model, realised bid/ask spreads or calibrated slippage. The 10 bps cost is an illustrative assumption and **not** an estimate of actual trading costs. Do not use the outputs as trading advice or forecasts.

## Repository map

```
index.html                    browser dashboard
web/                          self-contained charts and interactive JS analysis
src/research.py               Python signal, backtest and statistical diagnostics
data/                         attributed historical daily close snapshot
research/results.json         reproducible, fixed-protocol research result
research/METHODS.md           methodology and limitations
research/FINDINGS.md          the research narrative and actual observed results
scripts/rebuild_data.py       opt-in refresh from pinned hourly-data source
tests/                        unit, runtime-parity and Chromium UI tests
.github/workflows/            regression tests and automated static deployment
```

This is a research prototype, not a production trading system. Code is MIT-licensed; the source data is separately attributed and may have its own reuse conditions.