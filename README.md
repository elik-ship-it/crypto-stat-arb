This project tests whether a rolling-correlation pairs-trading strategy generates risk-adjusted returns in cryptocurrency markets, out-of-sample, net of realistic execution costs. Universe: top ~200–300 coins by trading volume. Method: walk-forward pair selection and mean-reversion signals on the spread. [Date range TBD once data is pulled.]
## Data

- Source: coin universe/ranking from CoinGecko (top 250 by trading volume); daily price + volume history from Yahoo Finance (yfinance).
- 205 of 250 coins had a matching Yahoo ticker (`SYMBOL-USD`); the rest were too new/small to be listed.
- Applied a ≥90% data-coverage filter over the 2-year window; 134 of 205 coins passed and form the working universe.
- Known limitation: Yahoo's crypto coverage skews toward larger, more liquid coins — this is a reasonable universe for a tradeable pairs strategy, but excludes long-tail microcap tokens.