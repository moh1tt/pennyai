# backend/server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import duckdb
import pandas as pd
from pathlib import Path

# Initialize FastAPI
app = FastAPI(title="Penny Stocks API")

# Enable CORS so frontend can access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend domain in production
    allow_methods=["*"],
    allow_headers=["*"]
)

# Path to DuckDB file
DB_PATH = Path("backend/data/duckdb/pennyai.duckdb")

# Endpoint to fetch penny stocks


@app.get("/api/pennystocks")
def get_pennystocks(limit: int = 100):
    # Connect to DuckDB
    conn = duckdb.connect(str(DB_PATH))

    query = f"""
        SELECT reddit_ticker
        FROM training
        LIMIT {limit}
    """

    try:
        df = conn.execute(query).fetchdf()
    except Exception as e:
        return {"error": str(e)}

    # Optional: summary stats
    total_stocks = len(df)

    # Convert DataFrame to list of dicts for JSON
    return {
        "totalStocks": total_stocks,

    }
