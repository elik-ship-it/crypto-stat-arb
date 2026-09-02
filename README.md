This project tests whether a rolling-correlation pairs-trading strategy generates risk-adjusted returns in cryptocurrency markets, out-of-sample, net of realistic execution costs. Universe: top ~200–300 coins by trading volume. Method: walk-forward pair selection and mean-reversion signals on the spread. [Date range TBD once data is pulled.]
## Data

- Source: coin universe/ranking from CoinGecko (top 250 by trading volume); daily price + volume history from Yahoo Finance (yfinance).
- 205 of 250 coins had a matching Yahoo ticker (`SYMBOL-USD`); the rest were too new/small to be listed.
- Applied a ≥90% data-coverage filter over the 2-year window; 134 of 205 coins passed and form the working universe.
- Known limitation: Yahoo's crypto coverage skews toward larger, more liquid coins — this is a reasonable universe for a tradeable pairs strategy, but excludes long-tail microcap tokens.
## Phase 2: Momentum vs. Reversal Decision

Tested average single-coin return autocorrelation across the 134-coin universe at
1-day, 1-week, 1-month, and 3-month horizons. None exceeded a rough significance
threshold (±0.0725 at this sample size), meaning individual coins show no reliable
own-return predictability at these horizons — expected in a reasonably efficient
market, and note the naive threshold likely understates the true noise given
cross-coin correlation via BTC beta.

This doesn't argue against a reversal strategy — it argues against expecting
single-asset momentum/reversal. Pairs trading targets the spread between two
correlated coins, a joint property that can be predictable even when each coin's
own return series looks like a random walk. Proceeding with rolling-correlation
pair selection (Phase 3) rather than a single-asset momentum strategy.
## Phase 3: Pair Selection

Selected pairs using a two-stage screen: rolling 180-day price-level correlation
(threshold 0.9, top-3 matches per coin) followed by an Engle-Granger cointegration
test (OLS residual spread, ADF p-value < 0.05). Correlation alone produced several
spurious matches driven by shared directional drift rather than a real relationship
(e.g. gas/vechain, correlation 0.97 but cointegration p-value 0.63) — the
cointegration screen filters these out. 143 candidate pairs tested, 87 passed both
screens; well above the ~7 expected by chance at a 5% threshold, suggesting real
signal rather than multiple-testing noise. Also excluded stablecoins/pegged assets
(USD- and EUR-pegged tokens, gold-backed tokens) as a separate category before
pair search, since their trivial near-flat price series otherwise dominates
correlation rankings without representing a tradeable relationship.
## Phase 4: Signal Generation

Computed 90-day rolling hedge ratio (beta), spread, and z-score for all 87 pairs.
Sanity-checked the top 3 pairs by cointegration p-value visually — z-scores
oscillate and repeatedly cross the ±1 entry threshold rather than trending or
sitting flat. Across all 87 pairs, mean threshold-crossing frequency (~29.6%)
closely matches the ~31.7% theoretical rate for a standard normal distribution,
supporting that spreads are behaving as genuine mean-reverting series rather
than artifacts. Crossing frequency varies noticeably by pair (47-277 out of
~640 valid days) — low-frequency pairs may reflect calmer spreads or,
alternatively, weaker mean-reversion than the in-sample cointegration test
suggested; worth revisiting if backtest performance looks weak for those pairs.
## Phase 5: Portfolio Construction

Converted z-scores into positions via a stateful entry/exit rule (enter at
|z|>1, exit at |z|<0.2, hold in between) rather than a per-day threshold rule,
since positions have memory. Sized each pair's position by its rolling hedge
ratio for dollar-neutrality, then equal-weighted across all 87 pairs to form
the portfolio (a simple starting design — risk-parity or cointegration-strength
weighting is a natural extension). Verified no look-ahead bias by using
yesterday's position to compute today's return. Resulting daily portfolio
returns: mean 0.039%, std 0.67% — a plausible, not yet cost-adjusted range.
## Phase 6: Execution Costs & Threshold Selection

Applied 20 bps cost per unit of position change. Net-of-cost annualized return
and Sharpe rise cleanly from exit=0.1 to exit=0.5 (Sharpe 0.44 -> 0.71 -> 1.06)
with roughly stable volatility. Exit=0.7 shows a much higher raw return but a
single day with a +31% portfolio return — investigation confirmed this is
driven by one pair on one day, not genuine strategy edge, so 0.7 was rejected
as fragile despite its nominally higher Sharpe (1.34). Selected exit=0.5 as
the working threshold going into the full backtest.
## Phase 7: Walk-Forward Backtest (Corrected)

Initial walk-forward result showed Sharpe -0.16, driven substantially by a
single-day -13.6% portfolio loss. Investigation traced this to a bad data
point in `meta-2-2` (single-day price ~10x off from surrounding days) and
revealed a broader pattern: several thinly-traded coins (monad,
jupiter-exchange-solana, openeden) showed repeated extreme single-day moves
consistent with unreliable Yahoo data rather than genuine volatility.

Added a filter excluding any coin with more than 2 days of >50% single-day
moves. Rerunning the walk-forward backtest on the cleaned universe:

- Annualized return: 5.37%
- Annualized volatility: 9.31%
- Sharpe ratio: 0.577
- Max daily loss: -3.3% (down from -13.6%)

Still meaningfully below the in-sample Sharpe of 1.06 from Phase 6 — expected,
since in-sample testing overstates performance by construction. The gap
between in-sample and walk-forward results is itself the project's central
finding: naive backtesting without a walk-forward structure and without data
quality screening would have produced a materially misleading conclusion in
either direction (falsely optimistic in-sample, falsely pessimistic before
the data fix).
## Phase 8: Performance Evaluation

Full walk-forward tear sheet (net of costs, cleaned data):

| Metric | Value |
|---|---|
| Annualized Return | 5.37% |
| Annualized Volatility | 9.31% |
| Sharpe Ratio | 0.577 |
| Max Drawdown | -10.11% |
| Max Drawdown Duration | 136 days (~6.5 months) |
| Total Return (period) | 9.46% |

A modest, realistic risk-adjusted return rather than a dramatic one — consistent
with Phase 7's period breakdown, which showed genuine regime dependence (roughly
half of rebalance periods positive, half negative) rather than uniform
outperformance. The 136-day drawdown duration is a meaningful practical
consideration: a real allocator would need to tolerate over half a year of
underwater performance before this strategy's edge reasserted itself.
## Phase 9: Benchmark Comparison & Purification

Compared walk-forward strategy returns against buy-and-hold BTC over the same
out-of-sample window:

| Metric | Value |
|---|---|
| Strategy Total Return | 9.46% |
| BTC Buy-and-Hold Total Return | -25.41% |
| Beta to BTC | 0.077 |
| Annualized Alpha | 6.15% |
| R-squared | 0.082 |
| Information Ratio (purified) | 0.689 |

Beta near zero and low R^2 confirm the strategy is genuinely close to
market-neutral by construction (dollar-neutral, hedge-ratio-sized positions),
not secretly carrying BTC exposure. The information ratio (0.689) exceeds the
raw Sharpe (0.577) precisely because so little of the strategy's volatility is
attributable to BTC — most of its risk is idiosyncratic to the pairs
themselves. Combined with Phase 7's overfitting diagnosis and data-quality
fix, this is the project's core result: a modest but genuine, largely
market-independent source of return, honestly arrived at rather than
overstated.

Note: OLS residuals always average to exactly zero by construction when the
regression includes an intercept, so the information ratio must be computed
as annualized alpha / annualized residual volatility — not from the mean of
the residuals directly.
## Phase 10: Clustering-Based Pair Selection (Differentiator)

Implemented K-means clustering as an alternative to Phase 3's correlation-
threshold pair candidate generation (flagged as unfinished future work in the
reference project), keeping the cointegration filter identical for a fair
comparison. Refactored the walk-forward engine into a reusable function
accepting any pair-selection method, verified to reproduce Phase 7's exact
result before running the comparison.

| Method | Ann. Return | Ann. Vol | Sharpe | Max DD |
|---|---|---|---|---|
| Correlation + Cointegration | 5.37% | 9.31% | 0.577 | -10.11% |
| K-Means + Cointegration | 9.04% | 9.22% | 0.980 | -6.56% |

K-means outperforms on every metric, and the improvement is robust (no single
outlier day driving it — worst-day comparison shows consistently milder tails,
not one lucky period). However, the honest driver is pair count, not smarter
selection: K-means averaged 607 candidate pairs per period vs. 132 for the
correlation method (a 4.6x difference), since it removes the 0.9 correlation
threshold as a pre-filter and lets cointegration alone decide validity. The
more precise conclusion: Phase 3's correlation threshold was likely too
restrictive, screening out many pairs that would have passed the (more
rigorous) cointegration test anyway. The result is better attributed to
increased diversification than to superior pair *quality* — a distinction
worth stating plainly rather than overclaiming.