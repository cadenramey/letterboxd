import pandas as pd
import feedparser
import re
from pathlib import Path

# ----------------------------
# CONFIG
# ----------------------------
USERNAME = "cramey14"
EXPORT_FILE = Path("diary.csv")  # full CSV export from Letterboxd
CSV_FILE = Path("letterboxd.csv")          # cleaned CSV to be used in Google Sheets

# Column names
COLUMNS = ["Watched Date", "Film", "Released", "My Rating", "Rewatch"]

# ----------------------------
# HELPERS
# ----------------------------
def canonical_title(title):
    """Canonical title used only for deduplication."""
    if pd.isna(title):
        return ""
    # Remove year/star rating in parentheses and lowercase
    return re.sub(r"\s*\(\d{4}\)\s*★?\d*\.?\d*", "", title.strip().lower())

def canonical_date(dt):
    """Normalize date to only the calendar day (no time)."""
    if pd.isna(dt):
        return pd.NaT
    return pd.to_datetime(dt).normalize()

# ----------------------------
# BOOTSTRAP CSV (first run)
# ----------------------------
if not CSV_FILE.exists():
    print("Bootstrap: Creating initial cleaned CSV from full export...")
    df = pd.read_csv(EXPORT_FILE)

    # Rename export columns to canonical names
    df = df.rename(columns={
        "Watched Date": "Watched Date",
        "Name": "Film",
        "Year": "Released",
        "Rating": "My Rating",
        "Rewatch": "Rewatch",
        "Letterboxd URI": "Film URL"  # ignored
    })

    # Keep only the desired columns
    df = df[["Watched Date", "Film", "Released", "My Rating", "Rewatch"]]

    # Normalize types
    df["Watched Date"] = pd.to_datetime(df["Watched Date"], errors="coerce")
    df["Released"] = pd.to_numeric(df["Released"], errors="coerce")  # float
    df["My Rating"] = pd.to_numeric(df["My Rating"], errors="coerce")

    # Rewatch: "Yes" -> True, everything else -> False
    df["Rewatch"] = df["Rewatch"].str.lower().map({"yes": True}).fillna(False).astype(bool)

    # Sort chronologically
    df = df.sort_values("Watched Date")
    df.to_csv(CSV_FILE, index=False)
    print(f"Bootstrap complete: {len(df)} rows saved.")

# ----------------------------
# WEEKLY RSS UPDATE
# ----------------------------
print("Fetching new RSS entries...")
df_existing = pd.read_csv(CSV_FILE)

# Normalize types
df_existing["Watched Date"] = pd.to_datetime(df_existing["Watched Date"], errors="coerce")
df_existing["Released"] = pd.to_numeric(df_existing["Released"], errors="coerce")  # float
df_existing["My Rating"] = pd.to_numeric(df_existing["My Rating"], errors="coerce")
df_existing["Rewatch"] = df_existing["Rewatch"].astype(bool)
df_existing["Film"] = df_existing["Film"].astype("string")

# Build deduplication set: (canonical title, date)
df_existing["CanonTitle"] = df_existing["Film"].apply(canonical_title)
df_existing["CanonDate"] = df_existing["Watched Date"].apply(canonical_date)
existing_pairs = set(zip(df_existing["CanonTitle"], df_existing["CanonDate"]))

# Fetch RSS feed
feed_url = f"https://letterboxd.com/{USERNAME}/rss/"
feed = feedparser.parse(feed_url)

rows = []

for entry in feed.entries:
    watched_date = canonical_date(entry.get("letterboxd_watcheddate"))
    film_title = entry.get("letterboxd_filmtitle")
    released = entry.get("letterboxd_filmyear")
    rewatch = entry.get("letterboxd_rewatch")
    my_rating = entry.get("letterboxd_memberrating")

    # Skip invalid entries
    if pd.isna(film_title) or pd.isna(watched_date):
        continue

    # Convert types
    released = pd.to_numeric(released, errors="coerce")  # float
    my_rating = pd.to_numeric(my_rating, errors="coerce")
    rewatch = str(rewatch).lower() == "yes"  # True/False

    # Deduplication key
    canon_title = canonical_title(film_title)
    canon_date = watched_date

    if (canon_title, canon_date) in existing_pairs:
        continue  # skip duplicates

    rows.append({
        "Watched Date": watched_date,
        "Film": film_title,
        "Released": released,
        "My Rating": my_rating,
        "Rewatch": rewatch
    })

if rows:
    df_new = pd.DataFrame(rows).reindex(columns=COLUMNS)
    df_all = pd.concat([df_existing, df_new], ignore_index=True)

    # Sort and optional safety deduplication
    df_all = df_all.sort_values("Watched Date")
    df_all = df_all.drop_duplicates(subset=["Film", "Watched Date"], keep="first")

    # Remove helper columns before saving
    df_all = df_all.drop(columns=["CanonTitle", "CanonDate"], errors="ignore")

    # Save
    df_all.to_csv(CSV_FILE, index=False)
    print(f"Added {len(df_new)} new entries. Total now: {len(df_all)} rows.")
else:
    print("No new RSS entries found. CSV unchanged.")
