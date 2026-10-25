# CarePoint Clinic - Selenium Automation (Python + pytest)

A complete practice project: a local clinic appointment website (`app/index.html`) plus Selenium tests for it.
The website is fictional. Use synthetic patient data only.

## 1. One-time setup (Linux container on Chromebook)

```bash
sudo apt update
sudo apt install -y chromium chromium-driver      # on some versions: chromium-browser chromium-chromedriver
chromium --version && chromedriver --version      # both versions should match

cd CarePoint_Selenium_Automation
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Look at the website yourself (optional)

```bash
python3 -m http.server 8000 --directory app
```
Open `http://localhost:8000` in the ChromeOS browser.

## 3. Run the automation

```bash
pytest -v                                   # runs all tests (the test fixture starts the website itself)
DEMO_DELAY=1 pytest -v -s                   # slow down 1 second per action so you can WATCH it
HEADLESS=1 pytest -v                        # force no browser window
HEADLESS=0 pytest -v                        # force a visible browser window
pytest -v --html=reports/report.html --self-contained-html   # HTML report
```
By default the browser window is visible if your container has a display, otherwise it runs headless.
Failed tests save a screenshot into `reports/`.

## What is tested (`tests/test_carepoint.py`)
- Doctor list is disabled until a specialty is chosen, and is filtered by specialty
- Selected date appears in the booking summary
- Valid booking shows a confirmation number
- Past date is rejected
- Missing patient name shows validation
- Invalid email is rejected
- Fully booked time slot is blocked
- Confirm button is enabled only for a valid form
- Confirmation window opens, closes, and shows booking details

## Structure
- `app/index.html` - the website
- `config/settings.py` - headless / delay / wait settings
- `utilities/driver_factory.py` - starts Chromium (works on Chromebook Linux)
- `utilities/server.py` - local web server used by the tests
- `pages/` - Page Object classes (`base_page.py`, `carepoint_page.py`)
- `tests/` - pytest tests and a unittest example
- `conftest.py` - fixtures and failure screenshots
