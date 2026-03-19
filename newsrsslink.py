import feedparser
import pandas as pd
from datetime import datetime, timedelta
import calendar
import time
import os
import random

# ----------------------------
# CONFIG
# ----------------------------
min_sleep = 2 
max_sleep = 5
start_year = 2021
end_year = 2026
output_csv = f"NIFTY50_news_{start_year}_to_{end_year}.csv"

nifty50_tickers = [
    "ADANIPORTS.NS","ASIANPAINT.NS","AXISBANK.NS","BAJAJ-AUTO.NS","BAJFINANCE.NS",
    "BAJAJFINSV.NS","BPCL.NS","BHARTIARTL.NS","BRITANNIA.NS","CIPLA.NS",
    "DIVISLAB.NS","DRREDDY.NS","EICHERMOT.NS","GRASIM.NS","HCLTECH.NS",
    "HDFCBANK.NS","HDFCLIFE.NS","HEROMOTOCO.NS","HINDALCO.NS",
    "HINDUNILVR.NS","ICICIBANK.NS","INDUSINDBK.NS","INFY.NS","ITC.NS",
    "JSWSTEEL.NS","KOTAKBANK.NS","LT.NS","M&M.NS","MARUTI.NS",
    "NESTLEIND.NS","NTPC.NS","ONGC.NS","POWERGRID.NS","RELIANCE.NS",
    "SBILIFE.NS","SBIN.NS","SUNPHARMA.NS","TCS.NS",
    "TATACONSUM.NS","TATAMOTORS.NS","TATASTEEL.NS","TECHM.NS",
    "TITAN.NS","ULTRACEMCO.NS","UPL.NS","WIPRO.NS"
]

def build_rss_url(ticker, start_date, end_date):
    clean_name = ticker.replace(".NS", "")
    query = f'{clean_name} after:{start_date} before:{end_date}'
    return "https://news.google.com/rss/search?q=" + query.replace(" ", "%20") + "&hl=en-IN&gl=IN&ceid=IN:en"

def fetch_google_news(ticker, start_date, end_date):
    rss_url = build_rss_url(ticker, start_date, end_date)
    feed = feedparser.parse(rss_url)
    records = []
    for entry in feed.entries:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published_dt = datetime(*entry.published_parsed[:6])
            pub_str = published_dt.strftime("%Y-%m-%d")
            if start_date <= pub_str < end_date:
                records.append({
                    "ticker": ticker,
                    "title": entry.get("title"),
                    "date": pub_str,
                    "source": entry.source.get("title") if "source" in entry else "Unknown",
                    "rss_link": entry.get("link"),  # ADDED: This saves the link to the article
                    "month_key": start_date[:7] 
                })
    time.sleep(random.uniform(min_sleep, max_sleep))
    return records

# ----------------------------
# RESUME LOGIC
# ----------------------------
processed_keys = set()
if os.path.exists(output_csv):
    try:
        df_existing = pd.read_csv(output_csv)
        if not df_existing.empty:
            # Ensure month_key exists for the set (it might be missing in older versions of your CSV)
            if 'ticker' in df_existing.columns and 'month_key' in df_existing.columns:
                df_existing['progress_key'] = df_existing['ticker'] + "_" + df_existing['month_key'].astype(str)
                processed_keys = set(df_existing['progress_key'].unique())
                print(f"Resuming: {len(processed_keys)} ticker-months already completed.")
    except Exception as e:
        print(f"Could not parse existing file, starting fresh: {e}")

# ----------------------------
# MAIN LOOP
# ----------------------------
today_str = datetime.today().strftime("%Y-%m-%d")

for year in range(start_year, end_year + 1):
    for month in range(1, 13):
        start_date_str = f"{year}-{month:02d}-01"
        end_day = calendar.monthrange(year, month)[1]
        end_date_str = (datetime(year, month, end_day) + timedelta(days=1)).strftime("%Y-%m-%d")

        if start_date_str > today_str:
            continue

        print(f"\n--- Checking Period: {year}-{month:02d} ---")

        for ticker in nifty50_tickers:
            current_key = f"{ticker}_{year}-{month:02d}"
            
            if current_key in processed_keys:
                continue

            print(f"  Fetching {ticker}...")
            try:
                news = fetch_google_news(ticker, start_date_str, end_date_str)
                
                if news:
                    df_new = pd.DataFrame(news)
                    header_needed = not os.path.exists(output_csv)
                    df_new.to_csv(output_csv, mode='a', index=False, header=header_needed)
                
                processed_keys.add(current_key)
            except Exception as e:
                print(f"  Error {ticker}: {e}")
                time.sleep(10)
                continue

print(f"\nExtraction Finished. Data is saved in {output_csv}")