import pandas as pd
import yfinance as yf
import os
from tqdm import tqdm


def enrich_tickers_with_yfinance(input_path, output_path):
    print("<--------------------------Running 3 -------------------------->")
    df = pd.read_parquet(input_path)
    tickers = df['tickers'].dropna().unique().tolist()
    print(f"Found {len(tickers)} unique tickers.")

    suffixes = ["", ".CN", ".V", ".TO", ".AX", ".L",
                ".NS", ".BO", ".SA", ".HK", ".NE", ".F"]

    all_data = []

    for ticker in tqdm(tickers, desc="Fetching ticker info from yfinance"):
        info = None
        final_symbol = None
        for suffix in suffixes:
            symbol = f"{ticker}{suffix}"
            try:
                stock = yf.Ticker(symbol)
                info = stock.info
                if info and "longName" in info:
                    final_symbol = symbol
                    break
            except Exception:
                continue

        if info and final_symbol:
            all_data.append({
                "reddit_ticker": ticker,
                "yfinance_symbol": final_symbol,
                "long_name": info.get("longName"),
                "short_name": info.get("shortName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "market_cap": info.get("marketCap"),
                "employees": info.get("fullTimeEmployees"),
                "founded": info.get("founded"),
                "country": info.get("country"),
                "currency": info.get("currency"),
                "current_price": info.get("currentPrice"),
                "previous_close": info.get("previousClose"),
                "open": info.get("open"),
                "day_high": info.get("dayHigh"),
                "day_low": info.get("dayLow"),
                "volume": info.get("volume"),
                "website": info.get("website"),
                "about": info.get("longBusinessSummary"),
            })
        else:
            all_data.append({
                "reddit_ticker": ticker,
                "yfinance_symbol": None,
                "error": "Not found"
            })

    df_tickers = pd.DataFrame(all_data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_tickers.to_parquet(output_path, engine="pyarrow", index=False)

    print(
        f"✅ Enriched ticker info saved to {output_path} ({len(df_tickers)} tickers total)")
