# server.py — Railway-compatible web server + in-process pipeline
import http.server
import os
import json
import threading
import logging
from datetime import datetime

PORT         = int(os.environ.get("PORT", 8000))
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN", "")   # set this in Railway env vars
PROJECT_ROOT  = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.join(PROJECT_ROOT, "dashboard")
DATA_JSON     = os.path.join(DASHBOARD_DIR, "dashboard_data.json")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# ── Pipeline state ─────────────────────────────────────────────────────────────
_lock             = threading.Lock()
_pipeline_running = False
_pipeline_status  = "idle"   # idle | running | done | error
_last_updated     = None


def run_pipeline():
    """Collect → clean → export, all in-process (no subprocess needed on Railway)."""
    global _pipeline_running, _pipeline_status, _last_updated
    logging.info("Pipeline started")

    try:
        # ── 1. Collect ─────────────────────────────────────────────────────
        from dotenv import load_dotenv
        from googleapiclient.discovery import build
        import pandas as pd
        import numpy as np

        load_dotenv()
        api_key = os.environ.get("YOUTUBE_API_KEY") or os.environ.get("YOUTUBE_API_KEY")
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY not set")

        youtube = build("youtube", "v3", developerKey=api_key)
        request = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            chart="mostPopular",
            regionCode="IN",
            maxResults=50
        )
        response = request.execute()

        rows = []
        for item in response.get("items", []):
            stats   = item.get("statistics", {})
            snippet = item.get("snippet", {})
            content = item.get("contentDetails", {})
            rows.append({
                "video_id"    : item["id"],
                "title"       : snippet.get("title"),
                "channel"     : snippet.get("channelTitle"),
                "category_id" : snippet.get("categoryId"),
                "published_at": snippet.get("publishedAt"),
                "views"       : stats.get("viewCount",    0),
                "likes"       : stats.get("likeCount",    0),
                "comments"    : stats.get("commentCount", 0),
                "duration"    : content.get("duration"),
            })

        df = pd.DataFrame(rows)
        logging.info(f"Collected {len(df)} videos")

        # ── 2. Clean ───────────────────────────────────────────────────────
        df["views"]    = pd.to_numeric(df["views"],    errors="coerce").fillna(0).astype(int)
        df["likes"]    = pd.to_numeric(df["likes"],    errors="coerce").fillna(0).astype(int)
        df["comments"] = pd.to_numeric(df["comments"], errors="coerce").fillna(0).astype(int)

        df["published_at"] = pd.to_datetime(df["published_at"])
        df["hour"]         = df["published_at"].dt.hour
        df["day_of_week"]  = df["published_at"].dt.day_name()
        df["month"]        = df["published_at"].dt.month_name()

        df["engagement_rate"] = (
            (df["likes"] + df["comments"]) / df["views"].replace(0, np.nan) * 100
        ).round(2)

        df.drop_duplicates(subset="video_id", inplace=True)
        df.dropna(subset=["title", "views"], inplace=True)

        # ── 3. Export JSON ─────────────────────────────────────────────────
        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        day_eng   = df.groupby("day_of_week")["engagement_rate"].mean().reindex(day_order).fillna(0).round(2)
        top10     = df.nlargest(10, "views")
        top_ch    = df.groupby("channel")["views"].sum().nlargest(10)
        hour_v    = df.groupby("hour")["views"].mean().round(0)
        cat_cnt   = df["category_id"].value_counts()

        data = {
            "total_videos"   : len(df),
            "total_views"    : int(df["views"].sum()),
            "avg_likes"      : int(df["likes"].mean()),
            "avg_engagement" : round(float(df["engagement_rate"].mean()), 2),
            "last_updated"   : datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),

            "top10_titles"   : [t[:40]+"..." if len(t)>40 else t for t in top10["title"].tolist()],
            "top10_views"    : top10["views"].tolist(),

            "days"           : day_order,
            "day_engagement" : day_eng.tolist(),

            "scatter"        : [{"x": int(r.views), "y": int(r.likes)} for r in df.itertuples()],

            "top_channels"   : top_ch.index.tolist(),
            "channel_views"  : [int(v) for v in top_ch.values.tolist()],

            "hours"          : [int(h) for h in hour_v.index.tolist()],
            "hour_views"     : [int(v) for v in hour_v.values.tolist()],

            "categories"     : [str(c) for c in cat_cnt.index.tolist()],
            "category_counts": cat_cnt.values.tolist(),
        }

        os.makedirs(DASHBOARD_DIR, exist_ok=True)
        with open(DATA_JSON, "w") as f:
            json.dump(data, f)

        _last_updated    = data["last_updated"]
        _pipeline_status = "done"
        logging.info(f"Pipeline done — {len(df)} videos, updated {_last_updated}")

    except Exception as e:
        _pipeline_status = "error"
        logging.error(f"Pipeline error: {e}")
    finally:
        _pipeline_running = False


def start_pipeline():
    global _pipeline_running, _pipeline_status
    with _lock:
        if _pipeline_running:
            return False
        _pipeline_running = True
        _pipeline_status  = "running"
    t = threading.Thread(target=run_pipeline, daemon=True)
    t.start()
    return True


# ── HTTP Handler ───────────────────────────────────────────────────────────────
class DashboardHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        path = self.path.split("?")[0]

        # /api/refresh?token=SECRET  — trigger pipeline
        if path == "/api/refresh":
            token = self._query_param("token")
            if REFRESH_TOKEN and token != REFRESH_TOKEN:
                self._json({"error": "Unauthorized"}, 401)
                return
            started = start_pipeline()
            self._json({"status": "started" if started else "running"})
            return

        # /api/status  — poll pipeline state
        if path == "/api/status":
            self._json({
                "status"      : _pipeline_status,
                "running"     : _pipeline_running,
                "last_updated": _last_updated,
            })
            return

        return super().do_GET()

    def end_headers(self):
        if "dashboard_data.json" in self.path:
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma",        "no-cache")
            self.send_header("Expires",       "0")
        super().end_headers()

    def _query_param(self, key):
        if "?" not in self.path:
            return ""
        qs = self.path.split("?", 1)[1]
        for part in qs.split("&"):
            if "=" in part:
                k, v = part.split("=", 1)
                if k == key:
                    return v
        return ""

    def _json(self, payload, code=200):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type",   "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control",  "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    os.chdir(DASHBOARD_DIR)

    # Auto-run pipeline once on startup so Railway always has fresh data on deploy
    logging.info("Running pipeline on startup...")
    start_pipeline()

    logging.info(f"Server on port {PORT}")
    with http.server.HTTPServer(("", PORT), DashboardHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
