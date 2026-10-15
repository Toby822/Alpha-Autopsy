# Start here — what Alpha Autopsy is doing

You do not need to know finance or Python to start.

Imagine you try **ten ways of predicting tomorrow's weather**. You test them against last year's weather, choose whichever looked best, and then check this year's weather. If your winner suddenly becomes useless, it probably learned patterns that didn't last.

That is this project, except with daily BTC/USDT prices and ten small rules.

## The experiment in five steps

1. **Take actual historical closes.** One BTC/USDT close a day from January 2024 to December 2025. These are facts about the historical market, not AI-generated prices.
2. **Write ten fixed rules.** Five say “follow recent price movement,” and five say “bet against it.” They look back 2, 5, 10, 20 or 40 days.
3. **Pick the winner using 2024 only.** The project ranks those ten rules by Sharpe ratio (average return divided by how much returns fluctuate, with an annualisation adjustment). The 2-day momentum rule wins the training period.
4. **Don't change the winner.** Check it against January–June 2025, then July–December 2025. The selected rule performs much worse than it did in the training period.
5. **Try to explain why.** Check how much turnover costs, whether the apparently good timing could be a coincidence and how uncertain the average daily return is.

## Words you'll see in the app

**Momentum:** If prices rose recently, bet they will keep rising; if they fell, bet they will keep falling.

**Reversal:** Take the opposite view; expect prices to bounce back.

**Training set:** The period where you choose what works.

**Validation set:** A later period that tells you whether the idea starts to fall apart. We use it only to report, not to reselect.

**Holdout / out-of-sample test:** A final period that should not be consulted while choosing the rule. Once you use it to redesign the rule, it is no longer untouched.

**Sharpe ratio:** A common but imperfect measure of average return relative to return volatility. A positive Sharpe in one short window isn't proof of a good strategy.

**Transaction costs:** Trading isn't free. This simple exercise assumes a fixed cost every time the position changes.

**Bootstrap interval:** A way to estimate how unstable the measured average return might be by resampling chunks of the observed data.

**Placebo test:** Break the original timing between prices and signal to see whether the observed alignment is unusual. Our test is informative but not a rigorous, fully adjusted strategy significance test.

## Where to look in the code

- `data/btcusdt_2024_2025_daily_close.csv` — the original historical daily prices supplied with this project.
- `src/research.py` — the research rules, dates, strategy returns, fees and statistics.
- `research/results.json` — the actual calculated results, written by Python.
- `web/engine.js` — recomputes those calculations inside a browser when you touch a control.
- `web/app.js` — draws the charts and reacts to your clicks.
- `web/style.css` — makes the page look the way it does.
- `index.html` — tells the browser where the titles, tables, charts and buttons go.
- `tests/` — checks that the code behaves as described.

## What to say if someone asks about it

Keep it natural. Say what you actually learned, not that you've built a profitable trading system:

> I wanted to understand how easy it is to fool yourself with a backtest. I compared ten simple momentum and reversal rules, selected the best one using 2024 data, then evaluated it on later dates without changing the rule. The selected signal lost most of its apparent advantage. I also checked trading costs, a timing placebo and uncertainty in the mean return. The point was to learn how to test a trading idea properly, including when it fails.

Before using this description in applications, make sure you can explain why `positions` in `src/research.py` uses yesterday's close rather than today's. That is one of the most important lines of the project.