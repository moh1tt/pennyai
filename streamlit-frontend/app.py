import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import math

# -----------------------------
# APP CONFIG
# -----------------------------
st.set_page_config(
    page_title="PennyAI",
    page_icon="",
    layout="wide",
)

# Add BEFORE st.title
st.markdown("""
    <style>
        /* Animated gradient keyframes */
        @keyframes gradientMove {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* Main background gradient */
        .stApp {
            background: linear-gradient(135deg, #0a0a0f, #101024, #0f1a3a);
            background-size: 200% 200%;
            animation: gradientMove 15s ease infinite;
        }

        /* Optional: widget containers */
        .css-18e3th9, .css-1d391kg {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border-radius: 12px;
            backdrop-filter: blur(6px);
        }

        /* Text tweaks */
        h1, h2, h3, p, span {
            color: #e8e8ff !important;
        }
    </style>
""", unsafe_allow_html=True)


st.title("PennyAI Stocks Dashboard and Analytics")
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
# KPI METRICS
# -----------------------------
# Most recent timestamp
last_updated = pd.to_datetime(df["created_utc"].max())

# Total distinct tickers
total_stocks = df["reddit_ticker"].nunique()

# Top mover (based on percent change)
if "percent_change" in df.columns:
    top_mover_row = df.loc[df["percent_change"].idxmax()]
else:
    df["percent_change"] = (
        (df["previous_close"] - df["open"]) / df["open"]) * 100
    top_mover_row = df.loc[df["percent_change"].idxmax()]

top_mover = top_mover_row["reddit_ticker"]
top_mover_change = round(top_mover_row["percent_change"], 2)

# Most talked-about ticker (count of mentions)
talk_counts = df["reddit_ticker"].value_counts()
most_talked = talk_counts.idxmax()
most_talked_count = talk_counts.max()

st.markdown("""
<style>
.kpi-card {
    background: rgba(255, 255, 255, 0.06);
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    backdrop-filter: blur(6px);
    border: 1px solid rgba(255, 255, 255, 0.12);
}
.kpi-title {
    font-size: 20px;
    color: #d8d8ff;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 32px;
    font-weight: bold;
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# DISPLAY KPI CARDS
# -----------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-title'>Total Stocks</div>
        <div class='kpi-value'>{total_stocks}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-title'>Top Mover</div>
        <div class='kpi-value'>{top_mover} ({top_mover_change}%)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-title'>Most Talked</div>
        <div class='kpi-value'>{most_talked} ({most_talked_count})</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-title'>Last Updated</div>
        <div class='kpi-value'>{last_updated.strftime("%Y-%m-%d %H:%M UTC")}</div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------
# LATEST NEWS
# -----------------------------
st.subheader("Latest Reddit Insights")

latest_df = df.sort_values("created_utc", ascending=False).head(20)

for _, row in latest_df.iterrows():
    sentiment_color = {
        "bullish": "#00ff95",
        "bearish": "#ff4b4b",
        "neutral": "#9ea7ff"
    }.get(str(row["verdict"]).lower(), "#cccccc")

    st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.05);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        border: 1px solid rgba(255,255,255,0.07);
    ">
        <div style="font-size:20px; font-weight:600; color:#b9e6ff;">
            {row['reddit_ticker']} — {row['long_name']} - ${row['current_price']} - {row['sector']}
        </div>
        <div style="font-size:14px; color:#7f9ebd; margin-bottom:8px;">
            {pd.to_datetime(row['created_utc'], unit='s').strftime('%Y-%m-%d %H:%M UTC')}
        </div>
        <div style="font-size:15px; color:#eaeafe;">
            {row['summarized_content']} <br> <br> {row['summarized_comments']} <a href="{row['website']}" target="_blank" style="color:#b9e6ff; text-decoration:underline;">
        {row['website']}
        </div>
        <div style="
            margin-top:10px;
            display:inline-block;
            padding:4px 10px;
            background:{sentiment_color};
            color:black;
            border-radius:8px;
            font-weight:600;
            font-size:12px;
        ">
            {row['verdict']}
        </div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("""
<style>
.footer {
    text-align: center;
    padding: 15px 0;
    font-size: 14px;
    color: #7f9ebd;
    border-top: 1px solid rgba(255,255,255,0.1);
    margin-top: 40px;
}
.footer a {
    color: #91e2ff;
    text-decoration: none;
    margin: 0 8px;
}
.footer a:hover {
    text-decoration: underline;
}
</style>

<div class="footer">
    Made by moh1tt | 
    <a href="https://www.linkedin.com/in/moh1tt" target="_blank">LinkedIn</a> | 
    <a href="mailto:mohitt.appari@gmail.com" target="_blank">Email</a> | 
    <a href="https://moh1tt.vercel.app" target="_blank">Website</a>
</div>
""", unsafe_allow_html=True)
