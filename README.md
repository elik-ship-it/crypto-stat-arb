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
