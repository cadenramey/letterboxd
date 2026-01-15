import feedparser
import pandas as pd

USERNAME = "cramey14"
OUTPUT_FILE = "letterboxd.csv"

feed_url = f"https://letterboxd.com/{USERNAME}/rss/"
feed = feedparser.parse(feed_url)

rows = []

for entry in feed.entries:
    rows.append({
        "Watched Date": entry.get("letterboxd_watcheddate"),
        "Film": entry.title,
        "Film URL": entry.link,
        "Logged At": entry.get("published")
    })

df = pd.DataFrame(rows)

# Sort oldest to newest
df["Watched Date"] = pd.to_datetime(df["Watched Date"], errors="coerce")
df = df.sort_values("Watched Date")

df.to_csv(OUTPUT_FILE, index=False)
print(f"Wrote {len(df)} rows to {OUTPUT_FILE}")
