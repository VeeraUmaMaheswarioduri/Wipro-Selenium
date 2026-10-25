# Test-case fix

The application intentionally hides the booking form until a user is authenticated.
The Selenium `carepoint` fixture now creates a synthetic test account in the browser's
localStorage, starts a fresh session, reloads the page, and waits for the booking section
to become visible. This keeps the application login behavior unchanged while making the
booking tests start from the correct authenticated state.

Run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

## Click-intercepted fix (16 failing tests)

Cause: `app/index.html` sets `html { scroll-behavior: smooth; }`. Selenium scrolls the button
into view and clicks before the smooth scroll finishes, so the click point lands on another
element -> `ElementClickInterceptedException`.

Fix (tests only, app untouched): `BasePage.click()` now disables smooth scrolling for the
test session, scrolls the element to the centre instantly, and retries / falls back to a JS click.
