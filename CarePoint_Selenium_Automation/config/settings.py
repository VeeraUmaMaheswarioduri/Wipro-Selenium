import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_FILE = PROJECT_ROOT / "app" / "index.html"
REPORTS_DIR = PROJECT_ROOT / "reports"
DATA_DIR = PROJECT_ROOT / "data"

EXPLICIT_WAIT_SECONDS = 45



def _headless_default():
    value = os.environ.get("HEADLESS")
    if value is not None:                      # HEADLESS=1 / HEADLESS=0 always wins
        return value == "1"
    # Not set: run headless only when the machine has no display (matches README).
    return os.name == "posix" and not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


HEADLESS = _headless_default()
DEMO_DELAY = float(os.environ.get("DEMO_DELAY", "0"))
