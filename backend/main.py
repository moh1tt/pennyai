from datetime import datetime

from scripts.fetch_posts_from_reddit import fetch_reddit_posts
from scripts.pre_process_reddit_posts import preprocess
from scripts.get_ticker_info_from_yfinance import enrich_tickers_with_yfinance
from scripts.merge_reddit_and_yfinance import merge_reddit_yfinance
from scripts.create_duckdb_from_parquet import upload_to_db
from scripts.create_summary_from_langchain import summarize_using_langchain

subreddits_to_fetch = ["pennystocks", "wallstreetbets", "smallstreetbets"]
today_str = datetime.today().strftime("%Y%m%d")

if __name__ == "__main__":
    fetch_reddit_posts(
        f"backend/data/reddit_posts_{today_str}.parquet",
        limit_per_sub=10, subreddit_list=subreddits_to_fetch)

    preprocess(f"backend/data/reddit_posts_{today_str}.parquet",
               f"backend/data/processed_reddit_posts_{today_str}.parquet")

    enrich_tickers_with_yfinance(
        f"backend/data/processed_reddit_posts_{today_str}.parquet", f"backend/data/processed_yfinance_info_{today_str}.parquet")

    merge_reddit_yfinance(
        f"backend/data/processed_reddit_posts_{today_str}.parquet",
        f"backend/data/processed_yfinance_info_{today_str}.parquet",
        f"backend/data/llm_ready_dataset_{today_str}.parquet"
    )

    upload_to_db("backend/data/duckdb/pennyai.duckdb",
                 f"backend/data/llm_ready_dataset_{today_str}.parquet",
                 "training")

    summarize_using_langchain("training")
