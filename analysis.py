from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import pandas as pd
import yfinance as yf

DEFAULT_TICKERS: List[str] = [
    "SUNDARMFIN.NS", "RPOWER.NS", "YESBANK.NS", "ZEEL.NS", "IDFCFIRSTB.NS", "PFC.NS",
    "NHPC.NS", "NMDC.NS", "BHEL.NS", "IEX.NS", "ONGC.NS", "GAIL.NS", "SAIL.NS",
    "IRCTC.NS", "MOTHERSON.NS", "BALRAMCHIN.NS", "RBLBANK.NS", "UCOBANK.NS", "BANKINDIA.NS",
    "MINDACORP.NS"
]

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_PATH = DATA_DIR / "recommendations.json"


def _fetch_history(ticker: str) -> Optional[pd.DataFrame]:
    try:
        hist = yf.Ticker(ticker).history(period="3mo", auto_adjust=False)
        if hist.empty:
            return None
        return hist
    except Exception:
        return None


def _build_row(ticker: str, hist: pd.DataFrame) -> Optional[dict]:
    close = hist["Close"].dropna()
    if len(close) < 20:
        return None

    current = float(close.iloc[-1])
    prev = float(close.iloc[-2]) if len(close) >= 2 else current
    prev5 = float(close.iloc[-5]) if len(close) >= 5 else current
    prev20 = float(close.iloc[-20]) if len(close) >= 20 else current
    ma20 = float(close.rolling(20).mean().iloc[-1])
    ma50 = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else ma20

    volume = float(hist["Volume"].iloc[-1]) if "Volume" in hist.columns else 0.0
    avg_volume = float(hist["Volume"].tail(20).mean()) if "Volume" in hist.columns else 0.0

    change_1d = ((current - prev) / prev) * 100 if prev else 0.0
    change_5d = ((current - prev5) / prev5) * 100 if prev5 else 0.0
    change_20d = ((current - prev20) / prev20) * 100 if prev20 else 0.0

    score = 0.0
    if current > ma20:
        score += 2.0
    if current > ma50:
        score += 1.0
    if change_1d > 0:
        score += 2.0
    if change_5d > 0:
        score += 2.0
    if volume > avg_volume * 1.3:
        score += 2.0
    if current < 5:
        score += 1.0
    if change_20d > -15:
        score += 1.0

    if score < 6.0:
        return None

    signal = "BUY" if change_1d > 0 and current > ma20 else "WATCH"
    reason = (
        "Strong momentum, above 20-day average, and volume confirmation"
        if signal == "BUY"
        else "Mixed momentum with a positive trend bias"
    )

    return {
        "ticker": ticker,
        "price": round(current, 2),
        "change_1d": round(change_1d, 2),
        "change_5d": round(change_5d, 2),
        "change_20d": round(change_20d, 2),
        "score": round(score, 1),
        "signal": signal,
        "reason": reason,
    }


def analyze_tickers(tickers: Optional[List[str]] = None, save_to_file: bool = True) -> pd.DataFrame:
    selected = list(tickers or DEFAULT_TICKERS)
    rows = []
    for ticker in selected:
        hist = _fetch_history(ticker)
        if hist is None:
            continue
        row = _build_row(ticker, hist)
        if row is not None:
            rows.append(row)

    if rows:
        df = pd.DataFrame(rows).sort_values(["score", "change_1d", "change_5d"], ascending=False)
        df = df.reset_index(drop=True)
    else:
        df = pd.DataFrame(columns=["ticker", "price", "change_1d", "change_5d", "change_20d", "score", "signal", "reason"])

    if save_to_file:
        DATA_DIR.mkdir(exist_ok=True)
        payload = {
            "generated_at": datetime.now().isoformat(),
            "recommendations": df.to_dict(orient="records"),
        }
        DATA_PATH.write_text(json.dumps(payload, indent=2))

    return df


def load_cached_recommendations() -> tuple[pd.DataFrame, Optional[str]]:
    if not DATA_PATH.exists():
        return pd.DataFrame(columns=["ticker", "price", "change_1d", "change_5d", "change_20d", "score", "signal", "reason"]), None

    try:
        payload = json.loads(DATA_PATH.read_text())
        rows = payload.get("recommendations", [])
        return pd.DataFrame(rows), payload.get("generated_at")
    except Exception:
        return pd.DataFrame(columns=["ticker", "price", "change_1d", "change_5d", "change_20d", "score", "signal", "reason"]), None


def get_daily_recommendations(force_refresh: bool = False) -> tuple[pd.DataFrame, Optional[str]]:
    if force_refresh:
        df = analyze_tickers(save_to_file=True)
        _, generated_at = load_cached_recommendations()
        return df, generated_at

    cached_df, generated_at = load_cached_recommendations()
    if cached_df is not None and not cached_df.empty and generated_at:
        try:
            cached_time = datetime.fromisoformat(generated_at)
            if datetime.now() - cached_time < timedelta(hours=24):
                return cached_df, generated_at
        except Exception:
            pass

    try:
        df = analyze_tickers(save_to_file=True)
        if not df.empty:
            _, generated_at = load_cached_recommendations()
            return df, generated_at
    except Exception:
        pass

    return cached_df, generated_at
