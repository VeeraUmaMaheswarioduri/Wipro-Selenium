"""Creates a Chrome/Chromium driver that works inside a Linux (Chromebook) container."""
import shutil

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from config.settings import HEADLESS

BROWSER_CANDIDATES = ["chromium", "chromium-browser", "google-chrome", "google-chrome-stable"]
DRIVER_CANDIDATES = ["chromedriver", "/usr/lib/chromium/chromedriver", "/usr/lib/chromium-browser/chromedriver"]


def _find(candidates):
    for name in candidates:
        path = shutil.which(name)
        if path:
            return path
    return None


def create_driver():
    options = Options()
    browser_path = _find(BROWSER_CANDIDATES)
    if browser_path:
        options.binary_location = browser_path
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--no-sandbox")              # needed inside the Linux container
    options.add_argument("--disable-dev-shm-usage")   # container has small /dev/shm
    options.add_argument("--disable-gpu")

    driver_path = _find(DRIVER_CANDIDATES)
    # Use the system chromedriver if installed (works on ARM Chromebooks too);
    # otherwise let Selenium Manager try to download one.
    service = Service(executable_path=driver_path) if driver_path else Service()
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(0)
    return driver
