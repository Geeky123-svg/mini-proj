import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# ============================
# Load environment variables from config/.env
# ============================
env_path = Path(__file__).resolve().parent.parent / 'config' / '.env'
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")     
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# ============================
# Step 1: Connect to default DB (postgres) to create target DB
# ============================
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        database="postgres",  # default db to create new db
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
except Exception as e:
    print("Error connecting to PostgreSQL:", e)
    exit(1)

# Create database if it doesn't exist
cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}';")
if not cur.fetchone():
    cur.execute(f"CREATE DATABASE {DB_NAME};")
    print(f"Database '{DB_NAME}' created successfully.")
else:
    print(f"Database '{DB_NAME}' already exists.")

cur.close()
conn.close()

# ============================
# Step 2: Connect to newly created database
# ============================
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.autocommit = True
    cur = conn.cursor()
except Exception as e:
    print("Error connecting to the new database:", e)
    exit(1)

# ============================
# Step 3: Enable TimescaleDB extension
# ============================
cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")

# ============================
# Step 4: Create tables
# ============================

cur.execute("""
CREATE TABLE IF NOT EXISTS stock_company (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    sector VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT now()
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS stock_price (
    stock_id INT REFERENCES stock_company(id),
    date DATE NOT NULL,
    open NUMERIC(10,2),
    high NUMERIC(10,2),
    low NUMERIC(10,2),
    close NUMERIC(10,2),
    adj_close NUMERIC(10,2),
    volume BIGINT,
    dividend NUMERIC(10,4),
    PRIMARY KEY(stock_id, date)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS index_price (
    date DATE PRIMARY KEY,
    open NUMERIC(10,2),
    high NUMERIC(10,2),
    low NUMERIC(10,2),
    close NUMERIC(10,2),
    adj_close NUMERIC(10,2),
    volume BIGINT
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS stock_prediction (
    stock_id INT REFERENCES stock_company(id),
    date DATE NOT NULL,
    horizon_days INT,
    model_version VARCHAR(20),
    predicted_price NUMERIC(10,2),
    predicted_return NUMERIC(8,4),
    actual_price NUMERIC(10,2),
    actual_return NUMERIC(8,4),
    created_at TIMESTAMP DEFAULT now(),
    PRIMARY KEY(stock_id, date, horizon_days, model_version)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS news (
    nid SERIAL PRIMARY KEY,
    stock_id INT REFERENCES stock_company(id),
    published_at TIMESTAMP,
    rss_link TEXT,
    title TEXT,
    content TEXT,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT now()
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS news_summary (
    sid SERIAL PRIMARY KEY,
    nid INT REFERENCES news(nid),
    summary TEXT,
    sentiment_score NUMERIC(5,2),
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT now()
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS stock_features (
    stock_id INT REFERENCES stock_company(id),
    date DATE,
    features JSONB,
    created_at TIMESTAMP DEFAULT now(),
    PRIMARY KEY(stock_id, date)
);
""")

# ============================
# Step 5: Convert to hypertables
# ============================
cur.execute("SELECT create_hypertable('stock_price', 'date', chunk_time_interval => interval '1 month', if_not_exists => TRUE);")
cur.execute("SELECT create_hypertable('index_price', 'date', chunk_time_interval => interval '1 month', if_not_exists => TRUE);")

# ============================
# Step 6: Create indexes
# ============================
cur.execute("CREATE INDEX IF NOT EXISTS idx_stock_price_stock_date ON stock_price(stock_id, date DESC);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_index_price_date ON index_price(date DESC);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_news_stock_date ON news(stock_id, published_at DESC);")

# ============================
# Step 7: Continuous aggregate (weekly)
# ============================
cur.execute("""
CREATE MATERIALIZED VIEW IF NOT EXISTS stock_price_weekly
WITH (timescaledb.continuous) AS
SELECT
    stock_id,
    time_bucket('7 days', date) AS week_start,
    AVG(adj_close) AS avg_close,
    SUM(volume) AS total_volume
FROM stock_price
GROUP BY stock_id, time_bucket('7 days', date);
""")

cur.execute("""
SELECT add_continuous_aggregate_policy('stock_price_weekly',
    start_offset => INTERVAL '1 month',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day');
""")

print(f"Database '{DB_NAME}' setup completed successfully!")

cur.close()
conn.close()