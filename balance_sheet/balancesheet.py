import yfinance as yf
import pandas as pd

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

def safe_get(bs, key):
    if key in bs.index:
        data = bs.loc[key]
        if not data.empty:
            return data.iloc[0]
    return None


rows = []

for ticker in nifty50_tickers:

    print(f"Fetching {ticker} report...")

    company = yf.Ticker(ticker)
    bs = company.balance_sheet

    if bs.empty:
        print(f"No data for {ticker}")
        continue

    rows.append({
        "company": ticker,
        "total_assets": safe_get(bs,"Total Assets"),
        "total_liabilities": safe_get(bs,"Total Liabilities Net Minority Interest"),
        "equity": safe_get(bs,"Total Stockholder Equity"),
        "total_debt": safe_get(bs,"Total Debt"),
        "long_term_debt": safe_get(bs,"Long Term Debt"),
        "cash": safe_get(bs,"Cash And Cash Equivalents"),
        "current_assets": safe_get(bs,"Current Assets"),
        "current_liabilities": safe_get(bs,"Current Liabilities"),
        "net_tangible_assets": safe_get(bs,"Net Tangible Assets")
    })

main_df = pd.DataFrame(rows)

main_df.to_csv("balance_sheet.csv", index=False)

print("Saved balance_sheet.csv")