from datetime import date, timedelta

import pytest

from pages.carepoint_page import doctor_matches

FUTURE = (date.today() + timedelta(days=7)).isoformat()
PAST = (date.today() - timedelta(days=3)).isoformat()


# ---------- Specialty / doctor filtering ----------
def test_doctor_dropdown_disabled_until_specialty_selected(carepoint):
    assert not carepoint.doctor_is_enabled()
    carepoint.select_specialty("Cardiology")
    assert carepoint.doctor_is_enabled()


def has_doctor(doctors, name):
    return any(doctor_matches(option, name) for option in doctors)


# Doctors shown for each specialty in app/index.html (the suffix like "(Spec)" is ignored).
SPECIALTY_DOCTORS = {
    "Cardiology": ["Dr. Asha Rao", "Dr. Ravi Kumar", "Dr. Kiran Reddy"],
    "Dermatology": ["Dr. Neha Das", "Dr. Ravi Nair", "Dr. Satish"],
    "Neurology": ["Dr. Imran Ali", "Dr. Sanjeev Raj", "Dr. Sandhya"],
    "Orthopedist": ["Dr. Amrutha", "Dr. Sampath"],
    "Gastroenterologist": ["Dr. Shiva Kumar", "Dr. Vikas Rajesh"],
    "Pulmonologist": ["Dr. Sankara Govind", "Dr. Arjun Raj"],
    "Gynecologist": ["Dr. Varshini", "Dr. Kavya"],
    "Diabetologist": ["Dr. Siddarth"],
    "Radiologist": ["Dr. Sanjay Kumar"],
    "Ophthalmologist": ["Dr. Ravi Krishna", "Dr. Narayana Reddy"],
}


def test_all_specialties_are_listed(carepoint):
    options = carepoint.specialty_options()
    for specialty in SPECIALTY_DOCTORS:
        assert specialty in options


@pytest.mark.parametrize("specialty", list(SPECIALTY_DOCTORS))
def test_each_specialty_shows_exactly_its_doctors(carepoint, specialty):
    carepoint.select_specialty(specialty)
    doctors = [d for d in carepoint.doctor_options() if not d.startswith("--")]
    expected = SPECIALTY_DOCTORS[specialty]
    assert len(doctors) == len(expected)
    for name in expected:
        assert has_doctor(doctors, name)


def test_filter_doctors_by_specialty(carepoint):
    carepoint.select_specialty("Cardiology")
    doctors = carepoint.doctor_options()
    assert has_doctor(doctors, "Dr. Asha Rao")
    assert has_doctor(doctors, "Dr. Ravi Kumar")
    assert not has_doctor(doctors, "Dr. Neha Das")      # Dermatology doctor must be filtered out
    assert not has_doctor(doctors, "Dr. Imran Ali")     # Neurology doctor must be filtered out


def test_doctor_names_show_their_level(carepoint):
    carepoint.select_specialty("Cardiology")
    doctors = carepoint.doctor_options()
    assert "Dr. Asha Rao(Spec)" in doctors
    assert "Dr. Ravi Kumar(Senior)" in doctors
    assert "Dr. Kiran Reddy(Junior)" in doctors


def test_changing_specialty_changes_doctor_list(carepoint):
    carepoint.select_specialty("Cardiology")
    carepoint.select_specialty("Neurology")
    doctors = carepoint.doctor_options()
    assert has_doctor(doctors, "Dr. Imran Ali")
    assert not has_doctor(doctors, "Dr. Asha Rao")


@pytest.mark.parametrize("specialty, doctor", [
    ("Orthopedist", "Dr. Amrutha"),
    ("Diabetologist", "Dr. Siddarth"),
    ("Ophthalmologist", "Dr. Narayana Reddy"),
])
def test_booking_works_for_the_new_specialties(carepoint, specialty, doctor):
    carepoint.fill_valid_booking(FUTURE, specialty=specialty, doctor=doctor)
    carepoint.confirm()
    assert "Confirmation number:" in carepoint.wait_for_message("Confirmation number:")
    assert carepoint.wait_for_text_contains(carepoint.SUMMARY, specialty)


# ---------- Date + booking ----------
def test_selected_date_appears_in_booking_summary(carepoint):
    carepoint.fill_valid_booking(FUTURE)
    carepoint.confirm()
    assert FUTURE in carepoint.wait_for_text_contains(carepoint.SUMMARY, FUTURE)


def test_valid_booking_shows_confirmation_number(carepoint):
    carepoint.fill_valid_booking(FUTURE)
    carepoint.confirm()
    assert "Confirmation number:" in carepoint.wait_for_message("Confirmation number:")


def test_past_date_is_rejected(carepoint):
    carepoint.fill_valid_booking(PAST)
    assert "future date" in carepoint.wait_for_message("future date").lower()
    assert not carepoint.is_enabled(carepoint.CONFIRM_BUTTON)


# ---------- Validation ----------
def test_missing_name_shows_validation(carepoint):
    carepoint.fill_valid_booking(FUTURE, name="")
    assert "name" in carepoint.wait_for_message("name").lower()
    assert not carepoint.is_enabled(carepoint.CONFIRM_BUTTON)


def test_invalid_email_is_rejected(carepoint):
    carepoint.fill_valid_booking(FUTURE, email="not-an-email")
    assert "valid email" in carepoint.wait_for_message("valid email").lower()
    assert not carepoint.is_enabled(carepoint.CONFIRM_BUTTON)


def test_full_slot_is_blocked(carepoint):
    carepoint.fill_valid_booking(FUTURE, time_slot="12:00 PM (Booked)")
    assert "booked" in carepoint.wait_for_message("booked").lower()
    assert not carepoint.is_enabled(carepoint.CONFIRM_BUTTON)


# ---------- Confirm button state ----------
def test_confirm_button_enabled_only_when_form_is_valid(carepoint):
    assert not carepoint.is_enabled(carepoint.CONFIRM_BUTTON)          # empty form
    carepoint.fill_valid_booking(FUTURE)
    carepoint.wait_until_enabled(carepoint.CONFIRM_BUTTON)
    assert carepoint.is_enabled(carepoint.CONFIRM_BUTTON)              # valid form
    carepoint.fill_patient("", "patient@example.com")
    carepoint.wait_until_disabled(carepoint.CONFIRM_BUTTON)
    assert not carepoint.is_enabled(carepoint.CONFIRM_BUTTON)          # invalid again


# ---------- Confirmation modal ----------
def test_confirmation_modal_opens_and_closes(carepoint):
    carepoint.open_confirmation_modal()
    assert carepoint.modal_is_visible()
    carepoint.close_confirmation_modal()
    assert carepoint.modal_is_hidden()


def test_modal_shows_booking_details_after_booking(carepoint):
    carepoint.fill_valid_booking(FUTURE)
    carepoint.confirm()
    carepoint.wait_for_message("Confirmation number:")
    carepoint.open_confirmation_modal()
    assert "CP-DEMO-1001" in carepoint.wait_for_text_contains(carepoint.MODAL_BODY, "CP-DEMO-1001")