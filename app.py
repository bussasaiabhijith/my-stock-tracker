import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta

from analysis import get_daily_recommendations, load_cached_recommendations


def get_recommendations(force_refresh: bool = False):
    result = get_daily_recommendations(force_refresh=force_refresh)
    if isinstance(result, tuple):
        return result
    return result, None


st.set_page_config(page_title="Penny Stock Radar", layout="wide")

st.title("🪙 Indian Penny Stock Radar")
india_tz = timezone(timedelta(hours=5, minutes=30))
now_text = datetime.now(india_tz).strftime('%Y-%m-%d %H:%M IST')
st.write(f"**Current time (IST):** {now_text}")

st.warning("This is for research and educational purposes only. Indian penny-stock ideas can be highly volatile and may lose value quickly. Consult a licensed financial advisor before investing.")

st.sidebar.header("Market Control")
st.sidebar.caption("This screen is designed to refresh daily before the Indian market opens, around 09:00 IST, and show the latest watchlist.")
refresh = st.sidebar.button("Refresh research")

if refresh:
    st.sidebar.success("Refreshing recommendation engine...")

with st.spinner("Scanning for momentum opportunities..."):
    df, generated_at = get_recommendations(force_refresh=refresh)

if df.empty:
    st.error("Unable to fetch fresh data right now. Showing the latest cached recommendations if available.")
    df, generated_at = load_cached_recommendations()

if generated_at:
    st.caption(f"Last research refresh: {generated_at}")

if not df.empty:
    st.subheader("Best Indian Penny Stock Candidates")
    display_df = df[["ticker", "price", "change_1d", "change_5d", "score", "signal", "reason"]].copy()
    display_df = display_df.rename(columns={
        "ticker": "Ticker",
        "price": "Price",
        "change_1d": "1D %",
        "change_5d": "5D %",
        "score": "Score",
        "signal": "Signal",
        "reason": "Why it stands out",
    })
    st.dataframe(display_df.head(10), use_container_width=True)

    st.subheader("Top Picks")
    best_pick = df.iloc[0]
    st.success(f"{best_pick['ticker']} is the strongest momentum watch today with a score of {best_pick['score']}.")
    st.write(f"Price: ₹{best_pick['price']:.2f} | 1D: {best_pick['change_1d']:.2f}% | 5D: {best_pick['change_5d']:.2f}%")
    st.write(best_pick['reason'])

    st.subheader("Quick Morning Research Notes")
    st.write("""
    - Watch for a strong opening drive and unusually high volume compared with the recent average.
    - Prefer Indian names that are trading above their 20-day moving average and showing positive 1D/5D momentum.
    - Keep position sizes small and set hard stop-loss levels because Indian penny stocks can gap violently.
    """)
else:
    st.info("No candidates met the current screening threshold.")
