import pandas as pd
from datetime import datetime
import os


def merge_reddit_yfinance(
    reddit_path: str,
    yfinance_path: str,
    output_path: str
):

    reddit_df = pd.read_parquet(reddit_path)
    yfin_df = pd.read_parquet(yfinance_path)

    reddit_df["tickers"] = reddit_df["tickers"].str.upper().str.strip()
    yfin_df["reddit_ticker"] = yfin_df["reddit_ticker"].str.upper().str.strip()

    merged_df = pd.merge(
        reddit_df,
        yfin_df,
        how="left",
        left_on="tickers",
        right_on="reddit_ticker"
    )

    merged_df["content_full"] = (
        merged_df["content"].fillna(
            "") + " " + merged_df["comments"].fillna("")
    ).str.strip()

    merged_df["last_updated"] = datetime.now()

    final_cols = [
        "reddit_ticker",
        "yfinance_symbol",
        "long_name",
        "short_name",
        "sector",
        "industry",
        "market_cap",
        "employees",
        "founded",
        "country",
        "currency",
        "current_price",
        "previous_close",
        "open",
        "day_high",
        "day_low",
        "volume",
        "website",
        "about",
        "score",
        "num_comments",
        "content",
        "comments",
        "created_utc",
        "error",
        "last_updated"
    ]

    final_df = merged_df[final_cols]
    final_df = final_df.sort_values(
        by=["created_utc", "score"],
        ascending=[False, False]
    ).reset_index(drop=True)

    final_df.to_parquet(output_path, engine="pyarrow", index=False)

    print(f"✅ Merged dataset saved to: {output_path}")
    print(f"🧩 Shape: {final_df.shape}")
