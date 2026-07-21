# my-stock-tracker
A daily Streamlit app that surfaces momentum-based penny-stock candidates before the market opens.

## What it does
- Screens a curated list of penny-stock tickers every time the app is refreshed.
- Uses recent price, momentum, and volume signals to rank candidates.
- Saves the latest recommendations so the site can keep showing a useful snapshot even if data refreshes are temporarily unavailable.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Notes
- The app uses Yahoo Finance data, so connectivity and ticker availability can affect results.
- This is research-oriented and should not be treated as financial advice.

