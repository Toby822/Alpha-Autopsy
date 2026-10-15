# Findings: the rule that looked promising, then didn't

## What I tested

Ten deliberately simple technical signals were compared on historical BTC/USDT futures-close observations. Five measures recent price direction over 2, 5, 10, 20 and 40 days; five take the other side. A 10-basis-point cost is charged for each unit of position turnover. The ranking used **2024 only**.

The experiment is not a search for a strategy to sell. The question is whether a straightforward in-sample selection process remains persuasive when time moves forward.

## The frozen result

**The 2-day momentum rule won the training search.** Its 2024 annualised sample Sharpe was about **+0.51**. That's not spectacular, but it was the highest of the ten trials under the predeclared assumptions.

It did not carry through:

| Period | Annualised sample Sharpe | Interpretation |
|---|---:|---|
| 2024 training | +0.51 | Selected from ten trials — upward selection bias is possible |
| Jan–Jun 2025 validation | −1.68 | A pronounced deterioration when tested forward |
| Jul–Dec 2025 holdout | −0.06 | No convincing support for a stable positive edge |

The final holdout's compounded hypothetical net return was approximately **−4.2%**. The moving-block bootstrap interval for the holdout's arithmetic average *daily* net return was roughly **[−26.9, +27.0] basis points**. It spans zero widely. A circular-shift placebo gave a one-sided diagnostic proportion of about **0.321**; do not treat this as a multiplicity-adjusted strategy p-value.

## What is and isn't learned

Some of the *other* signals had stronger holdout results. That observation cannot be used to quietly swap out the frozen winner and call the newly selected signal “validated.” Selecting the best holdout performer is a fresh hypothesis generated from the test set. It needs a genuinely new period to evaluate.

The result does not prove that momentum is impossible, or that market prices are completely unpredictable. It says this particular modest grid, this single asset, this history and these assumptions provided **no convincing forward validation for the training winner**.

A price-only test also cannot settle execution feasibility. The cost model is deliberately simple and excludes funding, spreads, latency and impact. Claims of live profitability would be unwarranted even if the test Sharpe had been positive.

## Next research question

**Does changing the decision horizon, using several instruments and estimating costs from actual executable quotes alter the conclusion?** The next study should pre-register its ideas, freeze the parameters and evaluate a future window that has not already been inspected.