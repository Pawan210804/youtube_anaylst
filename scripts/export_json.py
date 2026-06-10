# scripts/export_json.py

import pandas as pd
import json

df = pd.read_csv("data/cleaned/youtube_clean.csv")

day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
day_eng   = df.groupby("day_of_week")["engagement_rate"].mean().reindex(day_order).fillna(0).round(2)

top10 = df.nlargest(10, "views")

# Top 10 Channels by total views
top_channels = df.groupby("channel")["views"].sum().nlargest(10)

# Views by hour
hour_views = df.groupby("hour")["views"].mean().round(0)

# Category distribution
category_counts = df["category_id"].value_counts()

data = {
    "total_videos"    : len(df),
    "total_views"     : int(df["views"].sum()),
    "avg_likes"       : int(df["likes"].mean()),
    "avg_engagement"  : round(float(df["engagement_rate"].mean()), 2),

    # Top 10 videos
    "top10_titles"    : [t[:40] + "..." if len(t) > 40 else t for t in top10["title"].tolist()],
    "top10_views"     : top10["views"].tolist(),

    # Day engagement
    "days"            : day_order,
    "day_engagement"  : day_eng.tolist(),

    # Scatter
    "scatter"         : [{"x": int(r.views), "y": int(r.likes)} for r in df.itertuples()],

    # Top channels
    "top_channels"    : top_channels.index.tolist(),
    "channel_views"   : [int(v) for v in top_channels.values.tolist()],

    # Hour analysis
    "hours"           : [int(h) for h in hour_views.index.tolist()],
    "hour_views"      : [int(v) for v in hour_views.values.tolist()],

    # Category
    "categories"      : [str(c) for c in category_counts.index.tolist()],
    "category_counts" : category_counts.values.tolist(),
}

with open("dashboard/dashboard_data.json", "w") as f:
    json.dump(data, f)

print("✅ dashboard_data.json updated with more data!")