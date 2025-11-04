from datetime import datetime

from scripts.fetch_posts_from_reddit import fetch_reddit_posts
from scripts.pre_process_reddit_posts import preprocess
from scripts.get_ticker_info_from_yfinance import enrich_tickers_with_yfinance
from scripts.merge_reddit_and_yfinance import merge_reddit_yfinance
from scripts.create_duckdb_from_parquet import upload_to_db
from scripts.create_summary_from_langchain import summarize_using_langchain

subreddits_to_fetch = ["pennystocks", "wallstreetbets",
                       "smallstreetbets", "RobinHoodPennyStocks"]


def run_pipeline():
    print("✅ Fetching Reddit posts...")
    fetch_reddit_posts(
        "backend/data/reddit_posts.parquet",
        limit_per_sub=20,
        subreddit_list=subreddits_to_fetch,
        top_n=20,
    )

    print("✅ Preprocessing...")
    preprocess(
        "backend/data/reddit_posts.parquet",
        "backend/data/processed_reddit_posts.parquet",
    )

    print("✅ YFinance enrich...")
    enrich_tickers_with_yfinance(
        "backend/data/processed_reddit_posts.parquet",
        "backend/data/processed_yfinance_info.parquet",
    )

    print("✅ Merge datasets...")
    merge_reddit_yfinance(
        "backend/data/processed_reddit_posts.parquet",
        "backend/data/processed_yfinance_info.parquet",
        "backend/data/llm_ready_dataset.parquet",
    )

    print("✅ Uploading to DuckDB...")
    upload_to_db(
        "backend/data/duckdb/pennyai.duckdb",
        "backend/data/llm_ready_dataset.parquet",
        "training",
    )

    print("✅ Running LLM summaries...")
    summarize_using_langchain("training")

    print("🎉 Pipeline completed!")


if __name__ == "__main__":
    run_pipeline()
