"""Download two public daily OHLCV sample sets into data/ (both are survivorship-biased)."""
import os
import urllib.request

SETS = {
    "sp500_2013_2018.csv": "https://raw.githubusercontent.com/plotly/datasets/master/all_stocks_5yr.csv",
    "dow30_2006_2017.csv": "https://raw.githubusercontent.com/szrlee/Stock-Time-Series-Analysis/master/data/all_stocks_2006-01-01_to_2018-01-01.csv",
}
os.makedirs("data", exist_ok=True)
for name, url in SETS.items():
    path = os.path.join("data", name)
    if not os.path.exists(path):
        print("downloading", name)
        urllib.request.urlretrieve(url, path)
