import time
import requests
import pandas as pd
import yfinance as yf
from pathlib import Path

BASE_URL = "https://api.coingecko.com/api/v3"
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

def get_top_coins(n=250):
    """One lightweight, keyless call to CoinGecko just for the ranked coin list."""
    all_coins = []
    per_page = 250
    pages_needed = (n // per_page) + 1
    for page in range(1, pages_needed + 1):
        resp = requests.get(
            f"{BASE_URL}/coins/markets",
            params={"vs_currency": "usd", "order": "volume_desc", "per_page": per_page, "page": page},
        )
        resp.raise_for_status()
        all_coins.extend(resp.json())
        time.sleep(2)  # only 1-2 calls total, but stay polite
    return all_coins[:n]

if __name__ == "__main__":
    coins = get_top_coins(n=250)
    print(f"Got {len(coins)} coins ranked by volume from CoinGecko.")

    # Map coin symbol -> Yahoo ticker, de-duplicating symbols (some coins share tickers)
    seen_symbols = set()
    ticker_map = {}  # yahoo_ticker -> coingecko id (used for the filename)
    for coin in coins:
        symbol = coin["symbol"].upper()
        if symbol in seen_symbols:
            continue
        seen_symbols.add(symbol)
        ticker_map[f"{symbol}-USD"] = coin["id"]

    tickers = list(ticker_map.keys())
    print(f"Bulk downloading {len(tickers)} tickers from Yahoo Finance...")

    data = yf.download(tickers, period="2y", interval="1d", group_by="ticker", auto_adjust=False, threads=True)

    saved, skipped = 0, 0
    for yahoo_ticker, coin_id in ticker_map.items():
        try:
            df = data[yahoo_ticker][["Close", "Volume"]].dropna()
        except (KeyError, TypeError):
            skipped += 1
            continue
        if df.empty:
            skipped += 1
            continue
        df = df.reset_index()
        df.columns = ["date", "price", "volume"]
        df.to_csv(RAW_DIR / f"{coin_id}.csv", index=False)
        saved += 1

    print(f"Done. Saved {saved} coins, skipped {skipped} (not listed on Yahoo or no data).")