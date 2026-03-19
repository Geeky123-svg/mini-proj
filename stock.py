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
print(len(nifty50_tickers))
main_df = pd.DataFrame()

for ticker in nifty50_tickers:
    print(f"Fetching {ticker}...")

    stock = yf.Ticker(ticker)
    
    df = stock.history(
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d")
    )

    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
    company_name = stock.info.get("longName", ticker)

    # Clean filename (remove special characters)
    company_name = re.sub(r"[^\w\s-]", "", company_name)
    company_name = company_name.replace(" ", "_")

    #MMoving averages for 5, 10, 20, 50 days
    df['Company'] = company_name
    df['MA5'] = df['Close'].rolling(5).mean()
    df['MA10'] = df['Close'].rolling(10).mean()
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()


    #Momentum based features
    df['Return'] = df['Close'].pct_change()
    df['Momentum'] = df['Close'] - df['Close'].shift(5)
    df['ROC'] = df['Close'].pct_change(5)


    #Volatility Features
    df['Range'] = df['High']  - df['Low']
    df['Volatility'] = df['Close'].rolling(10).std()

    #Volume features
    df['Vol_MA10'] = df['Volume'].rolling(10).mean()
    df['Vol_Change'] = df['Volume'].pct_change()

    #Time features
    df['DayOfWeek'] = df['Date'].dt.dayofweek
    df['Month'] = df['Date'].dt.month

    #Exponential Moving Averages fo 10 and 20 days
    df['EMA10'] = df['Close'].ewm(span=10).mean()
    df['EMA20'] = df['Close'].ewm(span=20).mean()


    #New Price Features
    df['TypicalPrice'] = (df['High'] + df['Low'] + df['Close'])/3
    df['CO_Diff'] = df['Close'] - df['Open']
    

    if df.empty:
        print(f"⚠ No data for {ticker}")
        continue

    main_df = pd.concat([main_df, df])

    # Save CSV
    
main_df.to_csv('stock_data_5yrs.csv')

print("\n✅ All NIFTY 50 data saved by company name.")

