# scripts/clean.py

import pandas as pd
import numpy as np

# Load raw data
df = pd.read_csv("data/raw/youtube_trending.csv")

print("Raw data shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nMissing values:\n", df.isnull().sum())

# Convert numbers
df["views"]    = pd.to_numeric(df["views"],    errors="coerce").fillna(0).astype(int)
df["likes"]    = pd.to_numeric(df["likes"],    errors="coerce").fillna(0).astype(int)
df["comments"] = pd.to_numeric(df["comments"], errors="coerce").fillna(0).astype(int)

# Parse dates
df["published_at"] = pd.to_datetime(df["published_at"])
df["hour"]         = df["published_at"].dt.hour
df["day_of_week"]  = df["published_at"].dt.day_name()
df["month"]        = df["published_at"].dt.month_name()

# Engagement rate
df["engagement_rate"] = (
    (df["likes"] + df["comments"]) / df["views"].replace(0, np.nan) * 100
).round(2)

# Remove duplicates
df.drop_duplicates(subset="video_id", inplace=True)

# Drop nulls
df.dropna(subset=["title", "views"], inplace=True)

# Save cleaned data
df.to_csv("data/cleaned/youtube_clean.csv", index=False)

print("\n Cleaned data saved!")
print("Clean data shape:", df.shape)
print("\nSample:\n", df[["title","views","likes","engagement_rate"]].head())