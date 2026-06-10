# scripts/collect.py

import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
import pandas as pd

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError("❌ YOUTUBE_API_KEY not found! Make sure your .env file exists and has the key.")

youtube = build("youtube", "v3", developerKey=API_KEY)

def get_trending_videos():
    print("Fetching trending videos from YouTube...")
    
    request = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        chart="mostPopular",
        regionCode="IN",
        maxResults=50
    )
    response = request.execute()

    data = []
    for item in response["items"]:
        stats   = item.get("statistics", {})
        snippet = item.get("snippet", {})
        content = item.get("contentDetails", {})

        data.append({
            "video_id"    : item["id"],
            "title"       : snippet.get("title"),
            "channel"     : snippet.get("channelTitle"),
            "category_id" : snippet.get("categoryId"),
            "published_at": snippet.get("publishedAt"),
            "views"       : stats.get("viewCount",   0),
            "likes"       : stats.get("likeCount",   0),
            "comments"    : stats.get("commentCount",0),
            "duration"    : content.get("duration")
        })

    df = pd.DataFrame(data)
    df.to_csv("data/raw/youtube_trending.csv", index=False)
    print(f"Done! {len(df)} videos saved to data/raw/youtube_trending.csv")
    return df

df = get_trending_videos()
print(df.head())
