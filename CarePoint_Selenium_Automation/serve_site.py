from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent / "app"
PORT = 8000

handler = partial(SimpleHTTPRequestHandler, directory=str(APP_DIR))
server = ThreadingHTTPServer(("0.0.0.0", PORT), handler)
print("=" * 60)
print(" Jeevadhara website is running")
print(f"   Open in your browser:  http://localhost:{PORT}")
print(f"   If that fails, try:    http://penguin.linux.test:{PORT}")
print(" Press Ctrl + C to stop.")
print("=" * 60)
try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nStopped.")
