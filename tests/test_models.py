from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from rocamonti.exceptions import DataValidationError
from rocamonti.models import (
    DocumentType,
    Guest,
    Reservation,
    ReservationStatus,
    Room,
    RoomType,
)

VALID_RATE = Decimal(150000)


def test_valid_room():
    room = Room(101, RoomType.SINGLE, VALID_RATE)
    assert room.room_number == 101
    assert room.nightly_rate == Decimal("150000.00")


@pytest.mark.parametrize("bad_number", [0, -1, "101", True, 1.5])
def test_invalid_room_number(bad_number):
    with pytest.raises(DataValidationError, match="Room number"):
        Room(bad_number, RoomType.SINGLE, VALID_RATE)


@pytest.mark.parametrize("bad_type", ["Single", None, 1])
def test_invalid_room_type(bad_type):
    with pytest.raises(DataValidationError, match="room type"):
        Room(101, bad_type, VALID_RATE)


@pytest.mark.parametrize(
    "bad_rate",
    [100.0, "100", Decimal("0"), Decimal("-5"), Decimal("0.004"),
     Decimal("NaN"), Decimal("Infinity")],
)
def test_invalid_rate(bad_rate):
    with pytest.raises(DataValidationError, match="rate"):
        Room(101, RoomType.SINGLE, bad_rate)

def test_rate_rounds_half_up():
    assert Room(101, RoomType.SINGLE, Decimal("100.005")).nightly_rate == Decimal("100.01")


def test_valid_guest():
    guest= Guest("John Doe","johndoe@example.com","1234567890",DocumentType.PASSPORT,"A1234567")
    assert guest.name == "John Doe"
    assert guest.email == "johndoe@example.com"
    assert guest.phone_number == "1234567890"
    assert guest.document_type == DocumentType.PASSPORT
    assert guest.document_number == "A1234567"


@pytest.mark.parametrize("bad_name", ["", " ", None, 123])
def test_invalid_guest_name(bad_name):
    with pytest.raises(DataValidationError, match="Name"):
        Guest(bad_name, email="johndoe@example.com", 
            phone_number="1234567890", 
            document_type=DocumentType.PASSPORT, 
            document_number="A1234567")

@pytest.mark.parametrize("bad_email", ["", " ", None, 123, "johndoe", "johndoe@", "@example.com", 
                                       "johndoe@example", "johndoe@example.", "john doe@example.com", "a@b..c"])
def test_invalid_guest_email(bad_email):
    with pytest.raises(DataValidationError, match="Email"):
        Guest(name="John Doe", email=bad_email, 
            phone_number="1234567890", 
            document_type=DocumentType.PASSPORT, 
            document_number="A1234567")

@pytest.mark.parametrize("bad_phone",["", " ", None, 123, "123456", "abc-def-ghij"])
def test_invalid_guest_phone(bad_phone):
    with pytest.raises(DataValidationError, match="Phone number"):
        Guest(name="John Doe", email="johndoe@example.com", 
            phone_number= bad_phone, 
            document_type=DocumentType.PASSPORT, 
            document_number="A1234567")

@pytest.mark.parametrize("bad_document_type", [None, "Passport", 123, "", " "])
def test_invalid_guest_document_type(bad_document_type):
    with pytest.raises(DataValidationError, match="document type"):
        Guest(name="John Doe", email="johndoe@example.com", 
                        phone_number="1234567890", 
                        document_type=bad_document_type, 
                        document_number ="A1234567")

@pytest.mark.parametrize("bad_document_number", ["", " ", None, 123])
def test_invalid_guest_document_number(bad_document_number):
    with pytest.raises(DataValidationError, match= "Document number"):
        Guest(name="John Doe", email="johndoe@example.com", 
                phone_number="1234567890", 
                document_type=DocumentType.PASSPORT, 
                document_number =bad_document_number)


@pytest.mark.parametrize("email, raw_phone, expected_clean_phone", [("nombre.apellido+tag@dominio.co", "+573001234567", "+573001234567"),
        ("user123@sub.domain.org", "+1-800-555-0199", "+18005550199"),
        ("test@example.com", "(123) 456-7890", "1234567890")]) 

def test_valid_guest_special_formats(email, raw_phone, expected_clean_phone):
    guest = Guest(name="Jane Doe", email=email, 
                  phone_number=raw_phone, 
                  document_type=DocumentType.COLOMBIAN_ID_CARD, 
                  document_number="A1234567")
    assert guest.email == email.lower()
    assert guest.phone_number == expected_clean_phone
def test_actual_phone_format():
    guest = Guest(name="Jane Doe", email="jane@example.com", 
                  phone_number="310 762 8219", 
                  document_type=DocumentType.COLOMBIAN_ID_CARD, 
                  document_number="A1234567")
    assert guest.phone_number == "3107628219"


def test_guest_normalization():
    guest = Guest(name=" John Doe ", email="John.Doe@Example.com", 
                  phone_number=" 123-456-7890 ", 
                  document_type=DocumentType.PASSPORT, 
                  document_number=" a1234567 ")
    assert guest.name == "John Doe"
    assert guest.email == "john.doe@example.com"
    assert guest.phone_number == "1234567890"
    assert guest.document_number == "A1234567"


def test_guest_id_property():
    guest = Guest(name="John Doe", email="johndoe@example.com", 
                  phone_number="1234567890", 
                  document_type=DocumentType.PASSPORT, 
                  document_number="A1234567")
    assert guest.guest_id == "PASSPORT-A1234567"





@pytest.fixture
def sample_guest():
    return Guest("John Doe", "johndoe@example.com", "1234567890", DocumentType.PASSPORT, "A1234567")
@pytest.fixture
def sample_room():
    return Room(101, RoomType.SINGLE, Decimal("150000.00"))

def test_valid_reservation(sample_guest, sample_room):
    check_in = date.today() + timedelta(days=1)
    check_out = check_in + timedelta(days=2)
    res = Reservation(sample_guest, sample_room,check_in, check_out)

    assert res.guest == sample_guest
    assert res.room == sample_room
    assert res.nights == 2
    assert res.total_cost == Decimal("300000.00")
    assert res.status == ReservationStatus.CONFIRMED

def test_equal_dates(sample_guest, sample_room):
    check_in = date.today()
    check_out = check_in
    with pytest.raises(DataValidationError):
        Reservation(sample_guest, sample_room, check_in, check_out)

def test_check_out_before_check_in(sample_guest, sample_room):
    check_in = date.today()
    check_out = check_in - timedelta(days=1)
    with pytest.raises(DataValidationError):
        Reservation(sample_guest, sample_room, check_in, check_out)

@pytest.mark.parametrize("bad_check_in, bad_check_out", [
    ("2024-01-01", "2024-01-02"),
    (123, 456),
    (None, None),
    ("2024-01-01", None),
    (datetime.now(), datetime.now() + timedelta(days=1))
])
def test_bad_date(sample_guest, sample_room, bad_check_in, bad_check_out):
    with pytest.raises(DataValidationError):
        Reservation(sample_guest, sample_room, bad_check_in, bad_check_out)

def one_night_reservation(sample_guest, sample_room):
    check_in = date.today() + timedelta(days=1)
    check_out = check_in + timedelta(days=1)
    res = Reservation(sample_guest, sample_room, check_in, check_out)

    assert res.status == ReservationStatus.CONFIRMED
    assert res.nights == 1
    assert res.total_cost == sample_room.price