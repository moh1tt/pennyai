import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import math

# -----------------------------
# APP CONFIG
# -----------------------------
st.set_page_config(
    page_title="PennyAI Dashboard",
    page_icon="📈",
    layout="wide",
)

st.title("📊 PennyAI Stocks Dashboard")
st.markdown(
    "Real-time insights and trends on trending penny stocks from Reddit + Market Data")

# -----------------------------
# LOAD DATA
# -----------------------------


@st.cache_data
def load_data():
    conn = duckdb.connect("backend/data/duckdb/pennyai.duckdb", read_only=True)
    df = conn.execute("SELECT * FROM training").df()
    conn.close()
    return df


df = load_data()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("🔍 Filters")

sectors = ["All"] + sorted(df["sector"].dropna().unique().tolist())
countries = ["All"] + sorted(df["country"].dropna().unique().tolist())

selected_sector = st.sidebar.selectbox("Sector", sectors)
selected_country = st.sidebar.selectbox("Country", countries)
search_ticker = st.sidebar.text_input("Search Ticker or Symbol")

market_cap_min, market_cap_max = st.sidebar.slider(
    "Market Cap Range (USD)",
    int(df["market_cap"].min()),
    int(df["market_cap"].max()),
    (int(df["market_cap"].min()), int(df["market_cap"].max())),
    step=1_000_000,
)

# Apply filters
filtered = df.copy()
if selected_sector != "All":
    filtered = filtered[filtered["sector"] == selected_sector]
if selected_country != "All":
    filtered = filtered[filtered["country"] == selected_country]
filtered = filtered[
    (filtered["market_cap"] >= market_cap_min)
    & (filtered["market_cap"] <= market_cap_max)
]
if search_ticker:
    search_ticker = search_ticker.lower()
    filtered = filtered[
        filtered["reddit_ticker"].str.lower().str.contains(search_ticker)
        | filtered["yfinance_symbol"].str.lower().str.contains(search_ticker)
    ]

# -----------------------------
# KPI SUMMARY
# -----------------------------
st.markdown("### 📌 Market Summary")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Stocks", len(filtered))
col2.metric("Avg Price", f"${filtered['current_price'].mean():,.2f}")
col3.metric("Avg Market Cap", f"${filtered['market_cap'].mean():,.0f}")
col4.metric("Avg Volume", f"{filtered['volume'].mean():,.0f}")

# Top gainer
filtered["pct_change"] = (
    (filtered["current_price"] - filtered["previous_close"])
    / filtered["previous_close"]
) * 100
top_gainer = filtered.sort_values("pct_change", ascending=False).head(1)

if not top_gainer.empty:
    st.success(
        f"💹 **Top Gainer:** {top_gainer.iloc[0]['reddit_ticker']} "
        f"({top_gainer.iloc[0]['pct_change']:.2f}%)"
    )

# -----------------------------
# CHARTS
# -----------------------------
st.markdown("### 📊 Visual Insights")

chart1, chart2 = st.columns(2)

# Sector Distribution
sector_counts = (
    filtered.groupby("sector")[
        "reddit_ticker"].count().reset_index(name="count")
)
fig_sector = px.bar(
    sector_counts,
    x="sector",
    y="count",
    title="Companies per Sector",
    color="sector",
    text="count",
)
chart1.plotly_chart(fig_sector, use_container_width=True)

# Market Cap vs Price
fig_scatter = px.scatter(
    filtered,
    x="market_cap",
    y="current_price",
    color="sector",
    size="volume",
    hover_data=["long_name", "country"],
    title="Market Cap vs Current Price",
)
chart2.plotly_chart(fig_scatter, use_container_width=True)

# -----------------------------
# TOP MOVERS
# -----------------------------
st.markdown("### 🚀 Top Movers")
movers = filtered.sort_values("pct_change", ascending=False).head(10)
fig_movers = px.bar(
    movers,
    x="reddit_ticker",
    y="pct_change",
    color="pct_change",
    text="pct_change",
    title="Top 10 Daily Gainers",
)
st.plotly_chart(fig_movers, use_container_width=True)

# -----------------------------
# PAGINATED TABLE
# -----------------------------
st.markdown("### 🧾 Stock Details")

page_size = st.sidebar.number_input("Rows per page", 5, 50, 10)
total_pages = math.ceil(len(filtered) / page_size)
page = st.sidebar.number_input("Page", 1, total_pages, 1)

start_idx = (page - 1) * page_size
end_idx = start_idx + page_size
page_data = filtered.iloc[start_idx:end_idx]

st.dataframe(
    page_data[
        [
            "created_utc", "reddit_ticker", "yfinance_symbol", "long_name", "sector",
            "market_cap", "current_price", "previous_close", "volume", "pct_change"
        ]
    ].sort_values("market_cap", ascending=False),
    use_container_width=True,
)

# -----------------------------
# MODAL: SELECTED TICKER
# -----------------------------
st.markdown("### 🔎 Company Details")

selected_ticker = st.selectbox(
    "Select a ticker to view details",
    ["None"] + sorted(page_data["reddit_ticker"].unique().tolist()),
)

if selected_ticker != "None":
    details = filtered[filtered["reddit_ticker"] == selected_ticker].iloc[0]

    st.markdown(
        f"## 🏢 {details['reddit_ticker']} - {details.get('long_name', 'N/A')}")
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Price:** ${details['current_price']}")
        st.write(f"**Previous Close:** ${details['previous_close']}")
        st.write(f"**Market Cap:** ${details['market_cap']:,.0f}")
        st.write(f"**Volume:** {details['volume']:,.0f}")
        st.write(f"**Change:** {details['pct_change']:.2f}%")

    with col2:
        st.write(f"**Sector:** {details['sector']}")
        st.write(f"**Country:** {details['country']}")
        st.write(f"**Currency:** {details.get('currency', '—')}")
        st.write(f"**Employees:** {details.get('employees', '—')}")
        st.write(f"**Founded:** {details.get('founded', '—')}")

    st.markdown("---")
    st.markdown("#### 💬 LLM Summary")
    st.info(details.get("summarized_content", "No summary available."))

    st.markdown("#### 🧠 LLM Verdict")
    st.warning(details.get("verdict", "No verdict available."))

    if details.get("website"):
        st.markdown(f"[🌐 Visit Website]({details['website']})")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.caption(
    "💡 Data from Reddit sentiment + Yahoo Finance | Built with Streamlit + DuckDB + Plotly")
