import feedparser
import pandas as pd
from datetime import datetime, timedelta
import time

# ----------------------------
# CONFIG
# ----------------------------
company_name = "Infosys Limited"   # <-- Change company here
target_date = "2026-03-10"                   # Format: YYYY-MM-DD
sleep_seconds = 1
output_csv = f"{company_name.replace(' ', '_')}_{target_date}_news.csv"

# ----------------------------
# CHECK FUTURE DATE
# ----------------------------
today_str = datetime.today().strftime("%Y-%m-%d")

if target_date > today_str:
    print(f"Target date {target_date} is in the future. Skipping fetch.")
    exit()

# ----------------------------
# HELPER: Build Google RSS URL
# ----------------------------
def build_rss_url(company_name, date):
    start_date = date
    end_date = (
        datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)
    ).strftime("%Y-%m-%d")

    query = f'{company_name} after:{start_date} before:{end_date}'
    rss_url = (
        "https://news.google.com/rss/search?q="
        + query.replace(" ", "%20")
        + "&hl=en-IN&gl=IN&ceid=IN:en"
    )
    return rss_url

# ----------------------------
# FETCH GOOGLE NEWS
# ----------------------------
def fetch_google_news(company_name, date):
    rss_url = build_rss_url(company_name, date)
    print(f"Fetching news for {company_name}...")
    print(f"RSS URL: {rss_url}")

    feed = feedparser.parse(rss_url)
    records = []

    for entry in feed.entries:

        # Get published datetime
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published_dt = datetime(*entry.published_parsed[:6])
        else:
            continue

        # Filter exact date
        if published_dt.strftime("%Y-%m-%d") != date:
            continue

        # Get real news source
        source_name = None
        if "source" in entry:
            source_name = entry.source.get("title")

        records.append({
            "company": company_name,
            "title": entry.get("title"),
            "published": published_dt,
            "source": source_name,
            "link": entry.get("link")
        })

    time.sleep(sleep_seconds)
    return records

# ----------------------------
# MAIN
# ----------------------------
news_list = fetch_google_news(company_name, target_date)

# ----------------------------
# SAVE TO CSV
# ----------------------------
if news_list:
    df = pd.DataFrame(news_list)
else:
    df = pd.DataFrame(columns=["company", "title", "published", "source", "link"])
    print("No news found for this date.")

df.to_csv(output_csv, index=False)

print(f"\nSaved {len(df)} news items to {output_csv}")
