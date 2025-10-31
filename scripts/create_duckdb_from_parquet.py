import duckdb


def upload_to_db(DB_PATH, PARQUET_FILE, TABLE_NAME):
    print("<--------------------------Running 5 -------------------------->")

    con = duckdb.connect(DB_PATH)

    con.execute("CREATE SEQUENCE IF NOT EXISTS seq_row_id START 1;")

    # Create table with auto-increment primary key
    con.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        row_id INTEGER PRIMARY KEY DEFAULT nextval('seq_row_id'),
        reddit_ticker TEXT,
        yfinance_symbol TEXT,
        long_name TEXT,
        short_name TEXT,
        sector TEXT,
        industry TEXT,
        market_cap BIGINT,
        employees INTEGER,
        founded INTEGER,
        country TEXT,
        currency TEXT,
        current_price DOUBLE,
        previous_close DOUBLE,
        open DOUBLE,
        day_high DOUBLE,
        day_low DOUBLE,
        volume BIGINT,
        website TEXT,
        about TEXT,
        score INTEGER,
        num_comments INTEGER,
        content TEXT,
        comments TEXT,
        created_utc TIMESTAMP,
        error TEXT,
        last_updated TIMESTAMP
    );
    """)

    print("✅ Table created (or already existed).")

    con.execute(f"""
    INSERT INTO {TABLE_NAME} (
        reddit_ticker, yfinance_symbol, long_name, short_name,
        sector, industry, market_cap, employees, founded, country,
        currency, current_price, previous_close, open, day_high,
        day_low, volume, website, about, score, num_comments,
        content, comments, created_utc, error, last_updated
    )
    SELECT 
        reddit_ticker, yfinance_symbol, long_name, short_name,
        sector, industry, market_cap, employees, founded, country,
        currency, current_price, previous_close, open, day_high,
        day_low, volume, website, about, score, num_comments,
        content, comments, to_timestamp(created_utc) AS created_utc,
        error,
        last_updated
        FROM read_parquet('{PARQUET_FILE}');
        """)

    columns_to_add = [
        "summarized_content",
        "summarized_comments",
        "verdict"
    ]

    for col in columns_to_add:
        con.execute(f"""
            ALTER TABLE {TABLE_NAME} 
            ADD COLUMN IF NOT EXISTS {col} TEXT
        """)

    print("✅ Columns added (if not already present)")

    print("✅ Rows appended with auto-increment row_id.")

    result = con.execute(f"SELECT COUNT(*) FROM {TABLE_NAME};").fetchone()
    print(f"✅ {TABLE_NAME} row count: {result[0]}")

    preview = con.execute(f"SELECT * FROM  {TABLE_NAME} LIMIT 5;").fetchdf()
    print("\n✅ Sample rows:")
    print(preview)
