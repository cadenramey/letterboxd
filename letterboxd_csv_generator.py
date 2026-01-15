import pandas as pd

# Load Letterboxd's official export
df = pd.read_csv("letterboxd_diary.csv")

# Normalize columns (match your live CSV format)
df = df.rename(columns={
    "Watched Date": "Watched Date",
    "Name": "Film",
    "Year": "Released",
    "Rating": "My Rating",
    "Rewatch": "Rewatch",
    "Letterboxd URI": "Film URL"
})

df = df[["Watched Date", "Film", "Released", "My Rating", "Rewatch", "Film URL"]]

df["Watched Date"] = pd.to_datetime(df["Watched Date"], errors="coerce")
df = df.sort_values("Watched Date")

df.to_csv("letterboxd.csv", index=False)

