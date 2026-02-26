import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import re




# Date range (last 5 years)
end_date = datetime.today()
start_date = end_date - timedelta(days=5*365)
nifty50_tickers = [
    "ADANIPORTS.NS", "ASIANPAINT.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS",
    "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS", "BRITANNIA.NS", "CIPLA.NS",
    "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS", "EICHERMOT.NS", "GRASIM.NS",
    "HCLTECH.NS", "HDFCLIFE.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS",
    "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "INDUSINDBK.NS", "INFY.NS",
    "ITC.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS", "M&M.NS",
    "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS",
    "RELIANCE.NS", "SBILIFE.NS", "SHREECEM.NS", "SBIN.NS", "SUNPHARMA.NS",
    "TCS.NS", "TATACONSUM.NS", "TMPV.NS", "TATASTEEL.NS", "TECHM.NS",
    "TITAN.NS", "ULTRACEMCO.NS", "UPL.NS", "WIPRO.NS", "ADANIENT.NS"
]

main_df = pd.DataFrame()

for ticker in nifty50_tickers:
    print(f"Fetching {ticker}...")

    stock = yf.Ticker(ticker)

    
    df = stock.history(
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d")
    )

    company_name = stock.info.get("longName", ticker)

    # Clean filename (remove special characters)
    company_name = re.sub(r"[^\w\s-]", "", company_name)
    company_name = company_name.replace(" ", "_")

    df['Company'] = company_name
    if df.empty:
        print(f"⚠ No data for {ticker}")
        continue

    main_df = pd.concat([main_df, df])

    # Save CSV
    
main_df.to_csv('stock_data_5yrs.csv')

print("\n✅ All NIFTY 50 data saved by company name.")

