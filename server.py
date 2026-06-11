# server.py
# Place in PROJECT ROOT — run: python server.py
# Open: http://localhost:8000
# Dashboard loads INSTANTLY, data updates silently in background.

import http.server
import subprocess
import sys
import os
import logging
import threading
from datetime import datetime

PORT = 8000
PROJECT_ROOT   = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR  = os.path.join(PROJECT_ROOT, "dashboard")

logging.basicConfig(
    filename=os.path.join(PROJECT_ROOT, "server.log"),
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)

pipeline_running = False

def run_pipeline():
    global pipeline_running
    if pipeline_running:
        print("  [skip] Pipeline already running...")
        return
    pipeline_running = True

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Background update started...")
    logging.info("Background pipeline started")

    steps = [
        ("Fetching YouTube data...",  "scripts/collect.py"),
        ("Cleaning data...",          "scripts/clean.py"),
        ("Exporting to dashboard...", "scripts/export_json.py"),
    ]

    for label, script in steps:
        print(f"  >> {label}")
        result = subprocess.run(
            [sys.executable, os.path.join(PROJECT_ROOT, script)],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        if result.returncode != 0:
            print(f"  !! Failed: {script}\n{result.stderr}")
            logging.error(f"Failed at {script}: {result.stderr}")
            pipeline_running = False
            return

    print(f"  >> Done! Dashboard data is fresh.\n")
    logging.info("Pipeline completed")
    pipeline_running = False


class DashboardHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        # Serve the page IMMEDIATELY — pipeline runs in background thread
        if self.path in ("/", "/index.html"):
            threading.Thread(target=run_pipeline, daemon=True).start()

        super().do_GET()

    def end_headers(self):
        # Prevent browser from caching dashboard_data.json so stale data is never shown
        if "dashboard_data.json" in self.path:
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, format, *args):
        pass  # silence default access log


if __name__ == "__main__":
    os.chdir(DASHBOARD_DIR)

    print(f"╔══════════════════════════════════════╗")
    print(f"║   YouTube Dashboard Server Running   ║")
    print(f"╠══════════════════════════════════════╣")
    print(f"║  Open  →  http://localhost:{PORT}         ║")
    print(f"║  Page loads instantly                ║")
    print(f"║  Data updates silently in background ║")
    print(f"║  Stop  →  Ctrl+C                     ║")
    print(f"╚══════════════════════════════════════╝\n")

    with http.server.HTTPServer(("", PORT), DashboardHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
