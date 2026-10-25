import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from pages.base_page import BasePage


def _normalize(text):
    return re.sub(r"\s+", "", text).lower()


def doctor_matches(option_text, name):
    """True if a dropdown/list text such as 'Dr. Asha Rao(Spec)' belongs to doctor 'Dr. Asha Rao'.
    Ignores spaces and case, so 'Dr.Sampath(Junior)' matches 'Dr. Sampath' too."""
    return _normalize(option_text).startswith(_normalize(name))


class CarePointPage(BasePage):
    PLACE = (By.ID, "place")
    SPECIALTY = (By.ID, "specialty")
    DOCTOR = (By.ID, "doctor")
    DATE = (By.ID, "appointment-date")
    TIME = (By.ID, "time-slot")
    NAME = (By.ID, "patient-name")
    EMAIL = (By.ID, "patient-email")
    CONFIRM_BUTTON = (By.ID, "confirm-booking")
    MESSAGE = (By.ID, "form-message")
    SUMMARY = (By.ID, "booking-summary")
    MODAL = (By.ID, "confirmation-modal")
    WEEK_CHECKBOX = (By.ID, "book-week")
    BOOKING_COUNT = (By.ID, "booking-count")
    BOOKING_ITEMS = (By.CSS_SELECTOR, "#booking-list .booking-item")
    SLIDE_INDICATOR = (By.ID, "slide-indicator")
    PREV_SLIDE = (By.ID, "prev-slide")
    NEXT_SLIDE = (By.ID, "next-slide")
    CLEAR_BOOKINGS = (By.ID, "clear-bookings")
    MODAL_BODY = (By.ID, "modal-body")
    MODAL_CLOSE = (By.ID, "close-modal")
    REOPEN_MODAL = (By.ID, "reopen-modal")

    def open(self, url):
        self.driver.get(url)

    def login_as_test_user(self, url, name="Test Patient", email="patient@example.com", password="testpass123"):
        """Create a synthetic test user in the app's localStorage and start a clean session.

        The booking form is intentionally protected by the clinic's login UI. Tests that
        exercise booking behavior should start from an authenticated state rather than
        bypassing the application by editing its HTML. We seed only synthetic credentials
        in localStorage, then reload so the application's normal authentication code runs.
        """
        self.driver.get(url)
        self.driver.execute_script(
            "localStorage.clear();"
            "localStorage.setItem(arguments[0], JSON.stringify([{name: arguments[1], email: arguments[2], password: arguments[3]}]));"
            "localStorage.setItem(arguments[4], JSON.stringify(arguments[2]));",
            "jeevadhara.users.v1", name, email, password, "jeevadhara.session.v1"
        )
        self.driver.refresh()
        self.wait.until(lambda d: not d.find_element(By.ID, "booking-section").get_attribute("hidden"))

    def _select(self, locator):
        return Select(self.wait.until(lambda d: d.find_element(*locator)))

    def select_place(self, value):
        self._select(self.PLACE).select_by_visible_text(value)
        self.pause()

    def place_options(self):
        return [option.text for option in self._select(self.PLACE).options]

    def select_specialty(self, value):
        self._select(self.SPECIALTY).select_by_visible_text(value)
        self.pause()

    def _find_doctor_text(self, name):
        for option in Select(self.driver.find_element(*self.DOCTOR)).options:
            if option.text.strip() and doctor_matches(option.text, name):
                return option.text
        return None

    def select_doctor(self, name):
        """Select a doctor by name. 'Dr. Asha Rao' also selects 'Dr. Asha Rao(Spec)'."""
        # The doctor list is rebuilt by JavaScript after a specialty is chosen,
        # so wait until the doctor dropdown is enabled and contains the doctor.
        self.wait.until(lambda d: d.find_element(*self.DOCTOR).is_enabled()
                        and self._find_doctor_text(name) is not None)
        self._select(self.DOCTOR).select_by_visible_text(self._find_doctor_text(name))
        self.pause()

    def specialty_options(self):
        return [option.text for option in self._select(self.SPECIALTY).options]

    def doctor_is_enabled(self):
        return self.driver.find_element(*self.DOCTOR).is_enabled()

    def doctor_options(self):
        self.wait.until(lambda d: d.find_element(*self.DOCTOR).is_enabled())
        return [option.text for option in self._select(self.DOCTOR).options]

    def select_date(self, value):
        self.set_value_js(self.DATE, value)

    def select_time(self, value):
        self._select(self.TIME).select_by_visible_text(value)
        self.pause()

    def fill_patient(self, name, email):
        self.type_text(self.NAME, name)
        self.type_text(self.EMAIL, email)

    def fill_valid_booking(self, date_value, doctor="Dr. Asha Rao", specialty="Cardiology",
                           time_slot="10:00 AM", name="Test Patient", email="patient@example.com",
                           place="Kakinada"):
        if place:                      # place=None leaves the Place dropdown empty
            self.select_place(place)
        self.select_specialty(specialty)
        self.select_doctor(doctor)
        self.select_date(date_value)
        self.select_time(time_slot)
        self.fill_patient(name, email)

    def confirm(self):
        self.click(self.CONFIRM_BUTTON)

    def message(self):
        return self.get_text(self.MESSAGE)

    def wait_for_message(self, text):
        return self.wait_for_text_contains(self.MESSAGE, text)

    def summary(self):
        return self.get_text(self.SUMMARY)

    def open_confirmation_modal(self):
        self.click(self.REOPEN_MODAL)

    def close_confirmation_modal(self):
        self.click(self.MODAL_CLOSE)

    def modal_is_visible(self):
        return self.is_visible(self.MODAL)

    def modal_is_hidden(self):
        return self.wait_until_hidden(self.MODAL)

    # ---------- weekly booking + booking list slides ----------
    def enable_week_booking(self):
        checkbox = self.wait.until(lambda d: d.find_element(*self.WEEK_CHECKBOX))
        if not checkbox.is_selected():
            self.click(self.WEEK_CHECKBOX)

    def disable_week_booking(self):
        checkbox = self.wait.until(lambda d: d.find_element(*self.WEEK_CHECKBOX))
        if checkbox.is_selected():
            self.click(self.WEEK_CHECKBOX)

    def wait_for_booking_count(self, expected):
        self.wait.until(lambda d: d.find_element(*self.BOOKING_COUNT).text == str(expected))

    def booking_count(self):
        return int(self.get_text(self.BOOKING_COUNT))

    def slide_indicator(self):
        return self.get_text(self.SLIDE_INDICATOR)

    def visible_booking_texts(self):
        return [item.text for item in self.driver.find_elements(*self.BOOKING_ITEMS)]

    def next_slide(self):
        before = self.slide_indicator()
        self.click(self.NEXT_SLIDE)
        self.wait.until(lambda d: d.find_element(*self.SLIDE_INDICATOR).text != before)

    def prev_slide(self):
        before = self.slide_indicator()
        self.click(self.PREV_SLIDE)
        self.wait.until(lambda d: d.find_element(*self.SLIDE_INDICATOR).text != before)

    def next_is_enabled(self):
        return self.driver.find_element(*self.NEXT_SLIDE).is_enabled()

    def prev_is_enabled(self):
        return self.driver.find_element(*self.PREV_SLIDE).is_enabled()

    def all_booking_texts(self):
        """Walk through every slide (starting from slide 1) and collect all bookings."""
        texts = []
        while True:
            texts += self.visible_booking_texts()
            if not self.next_is_enabled():
                break
            self.next_slide()
        return texts

    def clear_bookings(self):
        self.click(self.CLEAR_BOOKINGS)