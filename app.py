import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="India Market Daily Tracker", layout="wide")

st.title("📈 Indian Market Daily Insights")
st.write(f"**Market Date:** {datetime.now().strftime('%Y-%m-%d')}")

# Disclaimer
st.warning("Disclaimer: This is an automated tool for analysis. Consult a financial advisor before investing.")

# Function to fetch data and give suggestions
def get_stock_analysis(tickers):
    data_list = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1mo")
            if hist.empty: continue
            
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            change = ((current_price - prev_price) / prev_price) * 100
            
            # Simple Logic for Suggestion
            # If RSI < 30 (Oversold) -> Buy | If RSI > 70 (Overbought) -> Sell
            # For this demo, we use Moving Average cross
            ma20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            
            if current_price > ma20:
                signal = "BUY / BULLISH"
                recommendation = "Invest for Long Term"
            else:
                signal = "SELL / BEARISH"
                recommendation = "Trade/Wait for Dip"
                
            data_list.append({
                "Stock": ticker.replace(".NS", ""),
                "Price": round(current_price, 2),
                "Change %": round(change, 2),
                "Signal": signal,
                "Strategy": recommendation
            })
        except:
            pass
    return pd.DataFrame(data_list)

# Sidebar for Selection
st.sidebar.header("Market Control")
market_type = st.sidebar.selectbox("Select Segment", ["Nifty 50", "Bank Nifty", "IT Sector"])

# List of Top Indian Stocks
nifty50_tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", 
                   "SBIN.NS", "BHARTIARTL.NS", "LTIM.NS", "ITC.NS", "HINDUNILVR.NS",
                   "TATAMOTORS.NS", "ADANIENT.NS", "AXISBANK.NS", "MARUTI.NS"]

st.subheader(f"Top 10 Recommendations for {market_type}")

with st.spinner('Analyzing Market Trends...'):
    df = get_stock_analysis(nifty50_tickers)
    
    if not df.empty:
        # Sort by best performers
        top_10 = df.head(10)
        
        # Display as a beautiful table
        st.table(top_10)
        
        # Visualizing the Top Buying Stocks
        st.subheader("Market Heatmap (Top 10)")
        st.bar_chart(df.set_index('Stock')['Change %'])
    else:
        st.error("Unable to fetch data. Please check your internet connection.")

# Daily Market Sentiment Section
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.info("### 💡 Today's Strategy")
    st.write("""
    - **Intraday Trading:** Better if the market opens with a gap up and stays above VWAP.
    - **Long Term:** Focus on blue-chip stocks like Reliance or HDFC if RSI is below 40.
    """)

with col2:
    st.success("### 🚀 Top Buying Pick")
    if not df.empty:
        best_pick = df.sort_values(by="Change %", ascending=False).iloc[0]
        st.write(f"**{best_pick['Stock']}** showing strong momentum at ₹{best_pick['Price']}")
