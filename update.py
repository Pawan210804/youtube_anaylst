# update.py
# Place this in your PROJECT ROOT (one level above dashboard/)
# Run: python update.py

import subprocess
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
import sys
import logging
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(
    filename=os.path.join(PROJECT_ROOT, "update.log"),
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)

def run_step(label, script_path):
    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"{'='*50}")
    logging.info(f"Starting: {label}")

    result = subprocess.run(
        [sys.executable, os.path.join(PROJECT_ROOT, script_path)],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT   # ← run from project root so all relative paths inside scripts work
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"⚠️  Warnings:\n{result.stderr}")

    if result.returncode != 0:
        print(f"❌ FAILED at: {script_path}")
        logging.error(f"Failed at {script_path}: {result.stderr}")
        sys.exit(1)

    logging.info(f"Completed: {label}")
    print("✅ Done!")

def main():
    start = datetime.now()
    print(f"\n🚀 YouTube Dashboard Update — {start.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("Manual pipeline started")

    run_step("🔄 Step 1 — Fetching fresh YouTube data...", "scripts/collect.py")
    run_step("🧹 Step 2 — Cleaning data...",               "scripts/clean.py")
    run_step("📊 Step 3 — Exporting to dashboard...",      "scripts/export_json.py")

    duration = (datetime.now() - start).seconds
    print(f"\n✅ All done in {duration}s!")
    print(f"   Open http://localhost:8000 to see fresh data\n")
    logging.info(f"Pipeline completed in {duration}s")

if __name__ == "__main__":
    main()
