"""Several bookings on the SAME day, in different places, with different doctors."""
import re
from datetime import date, timedelta

from pages.carepoint_page import doctor_matches

DAY = (date.today() + timedelta(days=7)).isoformat()


def book(page, expected_count, **kwargs):
    page.fill_valid_booking(DAY, **kwargs)
    page.confirm()
    page.wait_for_booking_count(expected_count)


def test_place_dropdown_lists_the_cities(carepoint):
    places = carepoint.place_options()
    for city in ("Kakinada", "Rajahmundry", "Visakhapatnam", "Vijayawada"):
        assert city in places


def test_place_is_required_to_enable_confirm(carepoint):
    carepoint.fill_valid_booking(DAY, place=None)          # everything except the place
    assert not carepoint.is_enabled(carepoint.CONFIRM_BUTTON)
    carepoint.select_place("Rajahmundry")
    carepoint.wait_until_enabled(carepoint.CONFIRM_BUTTON)
    assert carepoint.is_enabled(carepoint.CONFIRM_BUTTON)


def test_place_appears_in_summary_list_and_confirmation_window(carepoint):
    book(carepoint, 1, place="Kakinada")
    assert "Kakinada" in carepoint.summary()
    assert "Kakinada" in carepoint.visible_booking_texts()[0]
    carepoint.open_confirmation_modal()
    assert "Kakinada" in carepoint.wait_for_text_contains(carepoint.MODAL_BODY, "Kakinada")


def test_three_time_slots_booked_on_the_same_day(carepoint):
    numbers = []
    for index, slot in enumerate(["10:00 AM", "11:00 AM", "02:00 PM"], start=1):
        book(carepoint, index, time_slot=slot, name="Same Day Patient")
        numbers.append(re.search(r"CP-DEMO-\d+", carepoint.message()).group())
    assert numbers == ["CP-DEMO-1001", "CP-DEMO-1002", "CP-DEMO-1003"]
    texts = carepoint.all_booking_texts()
    assert [t.split(" | ")[1] for t in texts] == [DAY, DAY, DAY]          # same date
    assert [t.split(" | ")[2] for t in texts] == ["10:00 AM", "11:00 AM", "02:00 PM"]


def test_two_patients_can_see_two_doctors_at_the_same_time(carepoint):
    book(carepoint, 1, doctor="Dr. Asha Rao", time_slot="10:00 AM")
    book(carepoint, 2, doctor="Dr. Ravi Kumar", time_slot="10:00 AM",
         name="Second Patient", email="second@example.com")       # a different person
    doctors = [t.split(" | ")[3] for t in carepoint.visible_booking_texts()]
    assert len(doctors) == 2
    assert doctor_matches(doctors[0], "Dr. Asha Rao")
    assert doctor_matches(doctors[1], "Dr. Ravi Kumar")


def test_same_day_bookings_in_different_places(carepoint):
    book(carepoint, 1, place="Kakinada", doctor="Dr. Asha Rao", time_slot="10:00 AM")
    book(carepoint, 2, place="Rajahmundry", doctor="Dr. Ravi Kumar", time_slot="11:00 AM")
    book(carepoint, 3, place="Visakhapatnam", specialty="Neurology", doctor="Dr. Imran Ali",
         time_slot="02:00 PM")
    places = [t.split(" | ")[4] for t in carepoint.visible_booking_texts()]
    assert places == ["Kakinada", "Rajahmundry", "Visakhapatnam"]


def test_one_doctor_cannot_be_in_two_places_at_the_same_time(carepoint):
    book(carepoint, 1, place="Kakinada", doctor="Dr. Asha Rao", time_slot="10:00 AM")
    carepoint.select_place("Rajahmundry")                    # same doctor, date and time
    assert "booked" in carepoint.wait_for_message("booked").lower()
    assert not carepoint.is_enabled(carepoint.CONFIRM_BUTTON)


def test_fourth_booking_of_the_day_moves_to_the_second_slide(carepoint):
    for index, slot in enumerate(["10:00 AM", "11:00 AM", "02:00 PM"], start=1):
        book(carepoint, index, time_slot=slot)
    book(carepoint, 4, doctor="Dr. Ravi Kumar", time_slot="10:00 AM",
         name="Second Patient", email="second@example.com")       # a different person
    assert carepoint.slide_indicator() == "Slide 1 of 2"
    carepoint.next_slide()
    assert carepoint.slide_indicator() == "Slide 2 of 2"
    assert len(carepoint.visible_booking_texts()) == 1


# ---------- one person, many appointments, but never at the same time ----------
def test_same_person_cannot_have_two_appointments_at_the_same_time(carepoint):
    book(carepoint, 1, doctor="Dr. Asha Rao", time_slot="10:00 AM")
    carepoint.select_doctor("Dr. Ravi Kumar")                  # another doctor, same date, time and patient
    assert "already has an appointment" in carepoint.wait_for_message("already has an appointment")
    assert not carepoint.is_enabled(carepoint.CONFIRM_BUTTON)


def test_same_person_can_book_the_same_time_on_another_day(carepoint):
    book(carepoint, 1, time_slot="10:00 AM")
    next_day = (date.today() + timedelta(days=8)).isoformat()
    carepoint.fill_valid_booking(next_day, time_slot="10:00 AM")
    carepoint.confirm()
    carepoint.wait_for_booking_count(2)


def test_same_person_can_book_different_times_with_different_doctors(carepoint):
    book(carepoint, 1, doctor="Dr. Asha Rao", time_slot="10:00 AM")
    book(carepoint, 2, doctor="Dr. Ravi Kumar", time_slot="11:00 AM")
    assert carepoint.booking_count() == 2

