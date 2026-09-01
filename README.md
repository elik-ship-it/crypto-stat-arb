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