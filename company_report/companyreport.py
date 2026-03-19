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

print(len(nifty50_tickers))

main_df = pd.DataFrame()

for ticker in nifty50_tickers:
    
    print(f"Fetching {ticker} report...")

    company = yf.Ticker(ticker)
    report = company.info

    features = {
        "company_ticker": ticker,
        "marketCap": report.get("marketCap"),
        "pe_ratio": report.get("trailingPE"),
        "pb_ratio": report.get("priceToBook"),
        "roe": report.get("returnOnEquity"),
        "revenue_growth": report.get("revenueGrowth"),
        "debt_to_equity": report.get("debtToEquity"),
        "beta": report.get("beta")
    }

    df = pd.DataFrame([features])   # FIX

    main_df = pd.concat([main_df, df], ignore_index=True)

main_df.to_csv("company_reports.csv", index=False)

print("Saved company_reports.csv")