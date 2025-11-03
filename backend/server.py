# backend/server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import duckdb
import pandas as pd
from pathlib import Path
from datetime import datetime
import math

# Initialize FastAPI
app = FastAPI(title="Penny Stocks API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_methods=["*"],
    allow_headers=["*"]
)

DB_PATH = Path("backend/data/duckdb/pennyai.duckdb")

# ------------------ Helpers ------------------


def sanitize_value(v):
    """Convert NaN or inf to None for JSON serialization"""
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    return v


def sanitize_row(row: dict):
    """Apply sanitize_value to all values in a row dict"""
    return {k: sanitize_value(v) for k, v in row.items()}

# ------------------ Summary Endpoint ------------------


@app.get("/api/pennystocks/summary")
def get_summary():
    conn = duckdb.connect(str(DB_PATH))

    try:
        df = conn.execute("SELECT * FROM training").fetchdf()
    except Exception as e:
        return {"error": str(e)}

    if df.empty:
        return {
            "totalStocks": 0,
            "newStocksToday": 0,
            "topGainers": [],
            "trends": {}
        }

    # Total stocks
    total_stocks = len(df)

    # New stocks today
    today = datetime.utcnow().date()
    df["last_updated_date"] = pd.to_datetime(
        df["last_updated"], errors='coerce').dt.date
    new_stocks_today = df[df["last_updated_date"]
                          == today]["reddit_ticker"].nunique()

    # Top gainers (by % change)
    df["change_pct"] = (
        (df["current_price"] - df["previous_close"]) / df["previous_close"]) * 100
    top_gainers = (
        df.sort_values("change_pct", ascending=False)
        .head(5)[["reddit_ticker", "current_price", "change_pct"]]
        .applymap(sanitize_value)
        .to_dict(orient="records")
    )

    # Stock trends: last 30 updates per ticker
    trends = {}
    for ticker, group in df.groupby("reddit_ticker"):
        group_sorted = group.sort_values("last_updated").tail(30)
        trends[ticker] = [
            {"last_updated": str(row["last_updated"]), "current_price": sanitize_value(
                row["current_price"])}
            for _, row in group_sorted.iterrows()
        ]

    return {
        "totalStocks": total_stocks,
        "newStocksToday": new_stocks_today,
        "topGainers": top_gainers,
        "trends": trends,
    }

# ------------------ Details Endpoint ------------------
# ------------------ Details Endpoint ------------------


@app.get("/api/pennystocks/details")
def get_details(limit: int = None, include_comments: bool = True):
    """
    Returns all columns for all tickers.
    Parameters:
        - limit: optional integer to limit rows (useful for testing or pagination)
        - include_comments: whether to include comment content (can be large)
    """
    conn = duckdb.connect(str(DB_PATH))

    # All columns
    columns = [
        "row_id", "reddit_ticker", "yfinance_symbol", "long_name", "short_name",
        "sector", "industry", "market_cap", "employees", "founded", "country",
        "currency", "current_price", "previous_close", "open", "day_high",
        "day_low", "volume", "website", "about", "score", "num_comments",
        "content", "created_utc", "error", "last_updated",
        "summarized_content", "summarized_comments", "verdict"
    ]

    # Optionally exclude comments
    if not include_comments:
        columns = [c for c in columns if c not in [
            "content", "comments", "summarized_comments"]]

    query = f"SELECT {', '.join(columns)} FROM training ORDER BY last_updated DESC"
    if limit is not None:
        query += f" LIMIT {limit}"

    try:
        df = conn.execute(query).fetchdf()
    except Exception as e:
        return {"error": str(e)}

    # Replace NaN/inf with None for all numeric values
    import math

    def sanitize_value(v):
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            return None
        return v

    # Convert DataFrame to list of dicts, sanitizing every value
    full_data = []
    for row in df.to_dict(orient="records"):
        sanitized_row = {k: sanitize_value(v) for k, v in row.items()}
        full_data.append(sanitized_row)

    return {
        "totalStocks": len(df),
        "data": full_data
    }
