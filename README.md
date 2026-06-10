# YouTube Analysis Dashboard

A data pipeline and dashboard for tracking and analyzing trending YouTube videos in India — collecting stats, cleaning data, exporting reports, and visualizing insights.

Live repo: [github.com/Pawan210804/youtube_anaylst](https://github.com/Pawan210804/youtube_anaylst)

---

## Project Structure

```
youtube_analysis/
├── server.py              # Local web server for the dashboard
├── update.py              # Runs the full data pipeline
├── start.bat              # One-click start (Windows)
├── scripts/
│   ├── collect.py         # Fetches trending videos from YouTube API
│   ├── clean.py           # Cleans and normalizes raw data
│   ├── analyze.py         # Generates charts and analysis
│   ├── export_json.py     # Exports data for the dashboard
│   └── excel_report.py    # Generates Excel report
├── data/
│   ├── raw/               # Raw API responses (gitignored)
│   └── cleaned/           # Processed data (gitignored)
├── dashboard/
│   ├── index.html         # Dashboard UI
│   └── dashboard_data.json  # Generated data (gitignored)
└── output/
    └── charts/            # Generated chart images
```

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/Pawan210804/youtube_anaylst.git
cd youtube_anaylst
```

### 2. Install dependencies
```bash
pip install google-api-python-client pandas python-dotenv openpyxl matplotlib seaborn
```

### 3. Add your YouTube API key
Create a `.env` file in the project root:
```
YOUTUBE_API_KEY=your_api_key_here
```
Get a key from [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → YouTube Data API v3.

---

## Usage

### Run the full pipeline
```bash
python update.py
```
This fetches fresh YouTube trending data, cleans it, and exports it to the dashboard.

### Start the dashboard
```bash
python server.py
```
Then open [http://localhost:8000](http://localhost:8000) in your browser.

### One-click start (Windows)
Double-click `start.bat`

### Generate charts
```bash
python scripts/analyze.py
```

### Generate Excel report
```bash
python scripts/excel_report.py
```

---

## Outputs

| Output | Description |
|--------|-------------|
| `data/cleaned/youtube_clean.csv` | Cleaned video data |
| `dashboard/dashboard_data.json` | Data for the dashboard |
| `output/youtube_report.xlsx` | Excel report with 3 sheets |
| `output/charts/` | 5 analysis charts |

---

## Charts Generated

- Top 10 Trending Videos by Views
- Average Engagement Rate by Day of Week
- Correlation Heatmap
- Distribution of Views
- Views vs Likes Scatter Plot

---

## Security

- Never commit your `.env` file — it contains your secret API key
- `.gitignore` automatically blocks `.env`, `data/`, and generated files

---

## License

MIT
