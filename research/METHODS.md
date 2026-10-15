# Research protocol

## Question

Can a technical trading rule selected for its in-sample risk-adjusted performance retain that apparent advantage in chronologically later data?

**Null idea (informal):** the selected technical signal provides no reliably positive average returns after realistic friction. This project does not estimate a definitive null distribution for the *winner across multiple searches*, so none of its diagnostics establishes formal rejection of that null.

## Dataset and predeclared windows

Daily BTC/USDT futures-marked close prices from an attributed historical mirror, 2024–2025, 731 rows. Prices refer to the 23:00 UTC hourly close. See [provenance](../data/PROVENANCE.md).

| Window | Inclusive dates | Number of bars | Use |
|---|---|---:|---|
| TRAIN | 2024-01-01 to 2024-12-31 | 366 | Select the **single** winner by Sharpe |
| VALIDATE | 2025-01-01 to 2025-06-30 | 181 | Report forward-performance diagnostic; do not reselect |
| TEST | 2025-07-01 to 2025-12-31 | 184 | Final untouched holdout for the training winner |

Rules: momentum and reversal of last **2, 5, 10, 20 or 40 days** = exactly **10 candidates**. The universe and the default cost are held fixed in the `src/research.py` source.

## Signal and timing

For close \(C_t\), lookback \(L\) and interval return \(r_t=C_t/C_{t-1}-1\):

\[
 s_{t}^{\mathrm{momentum}}=\operatorname{sign}\left(\frac{C_{t-1}}{C_{t-1-L}}-1\right), \qquad s_t^{\mathrm{reversal}}=-s_t^{\mathrm{momentum}}.
\]

These are positions held over interval \((t-1,t]\). The first `L+1` observations have no available lookback and remain flat. The position calculation uses **no price after t−1**. Because we use daily closes, the fill-at-previous-close convention is a simplifying, idealised timing assumption, not a demonstrated achievable closing-auction or exchange execution.

## Cost and mark-to-market

Let \(s_t\in\{-1,0,+1\}\), turnover \(\tau_t=|s_t-s_{t-1}|\), and cost \(c\) in basis points **per unit of position change**. Daily gross and net strategy returns:

\[
 R_{t}^{\mathrm{gross}}=s_t r_t, \quad R_t^{\mathrm{net}}=s_t r_t - \tau_t\frac{c}{10,000}.
\]

Default \(c=10\) bps, as a deliberately **illustrative** combined friction proxy. A change from +1 to −1 costs 20 bps. Portfolio wealth is calculated as the compounded product \(W_T=\prod_t(1+R_t^{\mathrm{net}})\). The return strategy assumes short exposure is available at symmetric rates, without funding, liquidation margin, financing, funding-rate settlements, market impact, bid/ask data or borrowing constraints. It cannot establish executable net profitability.

The buy-and-hold reference is uncompensated underlying close-to-close return, with no transaction fees, to show market context rather than a fully comparable live benchmark. The Sharpe ratio uses arithmetic sample mean divided by sample standard deviation (`ddof=1`) times \(\sqrt{365}\) because the underlying market's reference dates include all calendar days. The project does not report a real daily-cash-rate-adjusted Sharpe; the zero-rate assumption is explicit.

## Selection protocol and multiplicity

All ten rules are ranked on **training Sharpe only**. The training winner is fixed **before** looking at validation or holdout returns. The code retains and displays every candidate and the sorting rule; it does not select the best test Sharpe after seeing outcomes. **No multiple-comparison-corrected significance test for the selected maximum** is claimed.

The app allows exploratory changes to strategy and cost. If you use holdout information to choose them, the test window becomes research data, no longer a valid pristine evaluation set for a newly tailored strategy. A *new, later* period would be required for an honest retest.

## Statistical diagnostics

**Circular-shift placebo.** In the final holdout only, hold positions and deterministic turnovers fixed. Circularly rotate the 184 daily underlying returns by each nonzero shift (183 alternatives), compute mean net return, and count how many have a mean no smaller than the original alignment. We show `(count + 1)/184` as a **one-sided diagnostic proportion**, not a validated strategy p-value. The procedure preserves the order and marginal distribution of the observed returns but breaks original calendar alignment. It does not account for selection among ten strategies or realistic conditioning of positions on shifted market history; don't use it to claim alpha discovery.

**Moving-block bootstrap.** Resample circular blocks of seven contiguous final-holdout **net daily returns** to form 1,000 length-matched bootstrap sequences (NumPy's fixed seed `72941`), then quote the empirical 2.5% and 97.5% quantiles of the *arithmetic daily mean* in basis points. Block resampling is an approximate diagnostic for serial dependence, not an interval for CAGR or an accurate distribution of future returns. The browser independently uses an in-browser deterministic block-bootstrap implementation for exploratory parameter changes; the original frozen result uses the Python-generated interval.

Other reported statistics: total compounded return, annualised sample Sharpe, simple hit rate, sum of absolute position changes and peak-to-trough mark-to-market drawdown.

## Engineering and reproducibility

The Python research engine generates `research/results.json`. The browser reads the frozen artifact and independently recalculates per-phase statistics in JavaScript. Unit tests check chronological coverage, lookahead safety, cost identity, frozen selection, reproducibility, parity between the two runtimes and DOM structure. Browser tests run the actual dashboard in Chromium, with research data injected locally to avoid reliance on external services.

The source data mirror has not been independently verified against exchange market data. One BTC instrument and roughly two years of price-only closes are insufficient for live trading inference. A more rigorous extension would require appropriately timestamped executable quotes, true fees/funding, explicit walk-forward re-selection, calibration windows, other instruments and an actually untouched future test period.