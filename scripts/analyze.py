# scripts/analyze.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load cleaned data
df = pd.read_csv("data/cleaned/youtube_clean.csv")

# Create charts folder
os.makedirs("output/charts", exist_ok=True)

print("=== YOUTUBE TRENDING ANALYSIS ===\n")

# 1. Basic Stats
print("📊 BASIC STATS:")
print(f"Total Videos     : {len(df)}")
print(f"Total Views      : {df['views'].sum():,}")
print(f"Average Views    : {int(df['views'].mean()):,}")
print(f"Average Likes    : {int(df['likes'].mean()):,}")
print(f"Average Comments : {int(df['comments'].mean()):,}")
print(f"Avg Engagement   : {df['engagement_rate'].mean():.2f}%")

# 2. Top 10 Videos by Views
print("\n🏆 TOP 10 VIDEOS BY VIEWS:")
top10 = df.nlargest(10, "views")[["title","views","likes","engagement_rate"]]
print(top10.to_string(index=False))

# 3. Best Day to Post
print("\n📅 BEST DAY TO POST:")
best_day = df.groupby("day_of_week")["engagement_rate"].mean().sort_values(ascending=False)
print(best_day)

# 4. Best Hour to Post
print("\n⏰ BEST HOUR TO POST:")
best_hour = df.groupby("hour")["views"].mean().sort_values(ascending=False).head(5)
print(best_hour)

# ============ CHARTS ============

# Chart 1 — Top 10 Videos by Views
plt.figure(figsize=(12, 6))
top10_chart = df.nlargest(10, "views")
sns.barplot(data=top10_chart, x="views", y="title", palette="viridis")
plt.title("Top 10 Trending Videos by Views", fontsize=16, fontweight="bold")
plt.xlabel("Views")
plt.ylabel("Video Title")
plt.tight_layout()
plt.savefig("output/charts/top10_views.png")
plt.show()
print("✅ Chart 1 saved: top10_views.png")

# Chart 2 — Engagement Rate by Day
plt.figure(figsize=(10, 5))
day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
day_data = df.groupby("day_of_week")["engagement_rate"].mean().reindex(day_order)
sns.barplot(x=day_data.index, y=day_data.values, palette="coolwarm")
plt.title("Average Engagement Rate by Day of Week", fontsize=16, fontweight="bold")
plt.xlabel("Day")
plt.ylabel("Engagement Rate (%)")
plt.tight_layout()
plt.savefig("output/charts/engagement_by_day.png")
plt.show()
print("✅ Chart 2 saved: engagement_by_day.png")

# Chart 3 — Correlation Heatmap
plt.figure(figsize=(8, 5))
sns.heatmap(
    df[["views","likes","comments","engagement_rate"]].corr(),
    annot=True, cmap="coolwarm", fmt=".2f"
)
plt.title("Correlation Heatmap", fontsize=16, fontweight="bold")
plt.tight_layout()
plt.savefig("output/charts/correlation_heatmap.png")
plt.show()
print("✅ Chart 3 saved: correlation_heatmap.png")

# Chart 4 — Views Distribution
plt.figure(figsize=(10, 5))
sns.histplot(df["views"], bins=20, color="steelblue", kde=True)
plt.title("Distribution of Views", fontsize=16, fontweight="bold")
plt.xlabel("Views")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig("output/charts/views_distribution.png")
plt.show()
print("✅ Chart 4 saved: views_distribution.png")

# Chart 5 — Views vs Likes Scatter
plt.figure(figsize=(10, 5))
sns.scatterplot(data=df, x="views", y="likes", hue="engagement_rate", palette="viridis", size="engagement_rate", sizes=(50,300))
plt.title("Views vs Likes", fontsize=16, fontweight="bold")
plt.xlabel("Views")
plt.ylabel("Likes")
plt.tight_layout()
plt.savefig("output/charts/views_vs_likes.png")
plt.show()
print("✅ Chart 5 saved: views_vs_likes.png")

print("\n🎉 ALL DONE! Check output/charts/ for all charts!")