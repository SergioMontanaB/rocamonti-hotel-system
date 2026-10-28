from decimal import Decimal
from datetime import date
import pytest
from src.models import Room, Guest, Reservation



def test_room_creation():
    room1 = Room(101, "Single", Decimal("100.00"))

    assert room1.room_number == 101
    assert room1.room_type == "Single"
    assert room1.nightly_rate == Decimal("100.00")

def test_room_creation_with_negative_rate():
    
    with pytest.raises(ValueError):
        Room(102, "Double", Decimal("-50.00"))
        
def test_room_creation_with_non_finite_rate():
    with pytest.raises(ValueError):
        Room(104, "Suite", Decimal("Infinity"))
    with pytest.raises(ValueError):
        Room(105, "Suite", Decimal("NaN"))

def test_room_creation_with_free_rate():
    with pytest.raises(ValueError):
        Room(103, "Suite", Decimal("0.00"))

def test_room_creation_with_invalid_room_number():
    with pytest.raises(ValueError):
        Room(-1, "Single", Decimal("100.00"))
    with pytest.raises(ValueError):
        Room(0, "Single", Decimal("100.00"))
    with pytest.raises(ValueError):
        Room("101", "Single", Decimal("100.00"))
    with pytest.raises(ValueError):
        Room(True, "Single", Decimal("100.00"))



def test_guest_creation():
    guest1 = Guest(1, "John Doe", "john.doe@example.com")

    assert guest1.guest_id == 1
    assert guest1.name == "John Doe"
    assert guest1.email == "john.doe@example.com"

def test_guest_creation_invalid_email():
    with pytest.raises(ValueError):
        Guest(2, "Jane Doe", "invalid-email")




def test_reservation_creation():
    guest1 = Guest(1, "John Doe", "john.doe@example.com")
    room1 = Room(101, "Single", Decimal("100.00"))
    reservation1 = Reservation(1, guest1, room1, date(2027, 1, 1), date(2027, 1, 10))

    assert reservation1.reservation_id == 1
    assert reservation1.guest == guest1
    assert reservation1.room == room1
    assert reservation1.check_in_date == date(2027, 1, 1)
    assert reservation1.check_out_date == date(2027, 1, 10)

def test_reservation_checkout_before_checkin():
    guest1 = Guest(1, "John Doe", "john.doe@example.com")
    room1 = Room(101, "Single", Decimal("100.00"))
    with pytest.raises(ValueError):
        Reservation(1, guest1, room1, date(2027, 1, 10), date(2027, 1, 1))

def test_reservation_duration_and_total_cost():
    guest1 = Guest(1, "John Doe", "john.doe@example.com")
    room1 = Room(101, "Single", Decimal("100.00"))
    reservation1= Reservation(1, guest1, room1, date(2027, 5, 10), date(2027, 5, 14))

    assert reservation1.duration == 4
    assert reservation1.total_cost == Decimal("400.00")

def test_reservation_with_non_date_objects():
    guest1 = Guest(1, "John Doe", "john.doe@example.com")
    room1 = Room(101, "Single", Decimal("100.00"))

    with pytest.raises(TypeError):
        Reservation(1, guest1, room1, "2027-01-01", "2027-01-10")

