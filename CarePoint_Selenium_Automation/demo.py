import os
os.environ.setdefault("HEADLESS", "0")
os.environ.setdefault("DEMO_DELAY", "10")

from datetime import date, timedelta

from selenium.webdriver.common.by import By

from config.settings import APP_FILE
from pages.carepoint_page import CarePointPage
from utilities.driver_factory import create_driver
from utilities.server import start_static_server

FUTURE = (date.today() + timedelta(days=7)).isoformat()

def step(text):
    print(f"\n>>> {text}")


server, url = start_static_server(APP_FILE.parent)
driver = create_driver()
try:
    page = CarePointPage(driver)
    step(f"Opening website: {url}")
    page.login_as_test_user(url)   # booking form is hidden until a user is logged in
    page.pause()

    step("1. Choose specialty: Cardiology (doctor list gets filtered)")
    page.select_specialty("Cardiology")
    print("   Doctors shown:", page.doctor_options())

    step("2. Choose doctor, date and time")
    page.select_doctor("Dr. Asha Rao")
    page.select_date(FUTURE)
    page.select_time("10:00 AM")

    step("3. Try an empty patient name -> validation message")
    page.fill_patient("", "patient@example.com")
    print("   Message:", page.message())

    step("4. Try an invalid email -> validation message")
    page.fill_patient("Test Patient", "not-an-email")
    print("   Message:", page.message())

    step("5. Choose the fully booked slot -> blocked")
    page.fill_patient("Test Patient", "patient@example.com")
    page.select_time("12:00 PM (Booked)")
    print("   Message:", page.wait_for_message("booked"))

    step("6. Choose a free slot and confirm the appointment")
    page.select_time("11:00 AM")
    page.wait_until_enabled(page.CONFIRM_BUTTON)
    page.confirm()
    print("   Message:", page.wait_for_message("Confirmation number:"))
    print("   Summary:", page.summary())

    step("7. Open and close the confirmation window")
    page.open_confirmation_modal()
    page.pause()
    modal = driver.find_element(By.ID, "confirmation-modal")
    print("   modal class:", repr(modal.get_attribute("class")), "| displayed:", modal.is_displayed())
    page.pause()
    page.close_confirmation_modal()

    print("\nDemo finished. The browser is still open - try the website by hand.")
    input("Press Enter here to close the browser... ")
finally:
    driver.quit()
    server.shutdown()
    server.server_close()

