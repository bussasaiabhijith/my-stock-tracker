from analysis import get_daily_recommendations

if __name__ == "__main__":
    df = get_daily_recommendations(force_refresh=True)
    print(f"Refreshed {len(df)} penny-stock recommendations")
