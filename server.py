# server.py
import http.server
import os

# Railway injects PORT as an environment variable
PORT = int(os.environ.get("PORT", 8000))

PROJECT_ROOT  = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.join(PROJECT_ROOT, "dashboard")


class DashboardHandler(http.server.SimpleHTTPRequestHandler):

    def end_headers(self):
        # Prevent browser caching of dashboard data
        if "dashboard_data.json" in self.path:
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, format, *args):
        pass  # silence access log


if __name__ == "__main__":
    os.chdir(DASHBOARD_DIR)
    print(f"Server running on port {PORT}")
    with http.server.HTTPServer(("", PORT), DashboardHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
