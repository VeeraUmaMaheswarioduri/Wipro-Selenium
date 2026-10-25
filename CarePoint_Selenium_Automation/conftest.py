import pytest

from config.settings import APP_FILE, EXPLICIT_WAIT_SECONDS, REPORTS_DIR
from utilities.driver_factory import create_driver
from utilities.server import start_static_server


@pytest.fixture(scope="session")
def app_url():
    server, url = start_static_server(APP_FILE.parent)
    yield url
    server.shutdown()
    server.server_close()


@pytest.fixture
def driver():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    browser = create_driver()
    yield browser
    try:
        browser.quit()
    except Exception:
        pass            # browser was already closed



@pytest.fixture
def carepoint(driver, app_url):
    from pages.carepoint_page import CarePointPage
    page = CarePointPage(driver, timeout=EXPLICIT_WAIT_SECONDS)
    # The real application requires authentication before the booking form is visible.
    # Start every test with a fresh synthetic account so booking tests are isolated.
    page.login_as_test_user(app_url)
    return page


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return
    browser = item.funcargs.get("driver")
    if not browser:
        return
    try:
        import base64
        png = browser.get_screenshot_as_png()
        shots = REPORTS_DIR / "screenshots"
        shots.mkdir(parents=True, exist_ok=True)
        status = "FAILED" if report.failed else "PASSED"
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in item.name)
        (shots / f"{status}_{safe_name}.png").write_bytes(png)
        from pytest_html import extras
        report.extras = getattr(report, "extras", []) + [
            extras.image(base64.b64encode(png).decode("ascii"), name=f"{status}: {item.name}")]
    except Exception:
        pass    # a screenshot problem must never crash pytest