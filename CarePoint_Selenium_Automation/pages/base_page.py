import time

from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config.settings import DEMO_DELAY


class BasePage:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def pause(self):
        if DEMO_DELAY:
            time.sleep(DEMO_DELAY)

    def _scroll_into_view(self, element):
        """Scroll instantly, ignoring the site's `html { scroll-behavior: smooth }`.

        With smooth scrolling Selenium computes the click point while the page is still
        animating, so the click lands on a different element and fails with
        ElementClickInterceptedException. The style tag is re-added on every call because
        a page reload throws it away.
        """
        self.driver.execute_script(
            "if (!document.getElementById('__no_smooth_scroll')) {"
            "  var s = document.createElement('style'); s.id = '__no_smooth_scroll';"
            "  s.textContent = 'html, body { scroll-behavior: auto !important; }';"
            "  document.head.appendChild(s); }"
            "arguments[0].scrollIntoView({block: 'center', inline: 'nearest', behavior: 'instant'});",
            element)

    def click(self, locator):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        self._scroll_into_view(element)
        try:
            element.click()
        except ElementClickInterceptedException:
            # Last resort (e.g. a CSS animation still moving the element): retry once
            # after it has settled, then fall back to a JS click.
            self.wait.until(EC.element_to_be_clickable(locator))
            try:
                self.driver.find_element(*locator).click()
            except ElementClickInterceptedException:
                self.driver.execute_script("arguments[0].click();", self.driver.find_element(*locator))
        self.pause()

    def type_text(self, locator, text):
        element = self.wait.until(EC.visibility_of_element_located(locator))
        element.clear()
        if text:
            element.send_keys(text)
        # Make sure the page's JS sees the change even when the text is empty.
        self.driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", element)
        self.pause()

    def set_value_js(self, locator, value):
        """Reliable way to fill <input type='date'> (typing depends on browser locale)."""
        element = self.wait.until(EC.presence_of_element_located(locator))
        self.driver.execute_script(
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", element, value)
        self.pause()

    def get_text(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator)).text

    def wait_for_text_contains(self, locator, text):
        self.wait.until(lambda d: text.lower() in d.find_element(*locator).text.lower())
        return self.get_text(locator)

    def is_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator)).is_displayed()

    def wait_until_hidden(self, locator):
        return self.wait.until(EC.invisibility_of_element_located(locator))

    def is_enabled(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator)).is_enabled()

    def wait_until_enabled(self, locator):
        self.wait.until(lambda d: d.find_element(*locator).is_enabled())

    def wait_until_disabled(self, locator):
        self.wait.until(lambda d: not d.find_element(*locator).is_enabled())

    def get_attribute(self, locator, name):
        return self.wait.until(EC.presence_of_element_located(locator)).get_attribute(name)
