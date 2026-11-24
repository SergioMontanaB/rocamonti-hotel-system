from datetime import date
from decimal import Decimal

import pytest

from rocamonti.exceptions import ConflictError, NotFoundError, RoomNotFoundError
from rocamonti.hotel import Hotel
from rocamonti.models import (
    DocumentType,
    Guest,
    Reservation,
    ReservationStatus,
    Room,
    RoomType,
)


@pytest.fixture
def hotel():
    """Creates a hotel new and clean hotel instance."""
    return Hotel()


@pytest.fixture
def sample_room():
    return Room(
        room_number=101, room_type=RoomType.SINGLE, nightly_rate=Decimal("100.00")
    )


@pytest.fixture
def sample_guest():
    return Guest(
        name="John Doe",
        email="john@example.com",
        phone_number="1234567890",
        document_type=DocumentType.PASSPORT,
        document_number="A12345",
    )


def test_add_valid_room(hotel, sample_room):
    hotel.add_room(sample_room)
    assert hotel.get_room(101) == sample_room


def test_add_duplicate_room_raises_error(hotel, sample_room):
    room2 = Room(
        room_number=101, room_type=RoomType.SINGLE, nightly_rate=Decimal("100.00")
    )
    hotel.add_room(sample_room)
    with pytest.raises(ConflictError):
        hotel.add_room(room2)


def test_get_nonexistent_room(hotel):
    with pytest.raises(RoomNotFoundError):
        hotel.get_room(999)


def test_valid_register_guest(hotel, sample_guest):
    hotel.register_guest(sample_guest)
    assert hotel.get_guest("PASSPORT-A12345") == sample_guest


def test_register_duplicate_guest(hotel, sample_guest):
    hotel.register_guest(sample_guest)
    guest2 = Guest(
        name="John Doe",
        email="john@example.com",
        phone_number="1234567890",
        document_type=DocumentType.PASSPORT,
        document_number="A12345",
    )
    with pytest.raises(ConflictError):
        hotel.register_guest(guest2)


def test_get_nonexistent_guest(hotel):
    with pytest.raises(NotFoundError):
        hotel.get_guest("PASSPORT-XYZ")


def test_list_all_guests(hotel, sample_guest):
    guest2 = Guest(
        name="Jane Doe",
        email="jane@example.com",
        phone_number="0987654321",
        document_type=DocumentType.PASSPORT,
        document_number="B12345",
    )
    hotel.register_guest(sample_guest)
    hotel.register_guest(guest2)

    assert hotel.list_all_guests() == [sample_guest, guest2]


def test_list_all_rooms(hotel, sample_room):
    room2 = Room(
        room_number=102, room_type=RoomType.SINGLE, nightly_rate=Decimal("100.00")
    )
    hotel.add_room(sample_room)
    hotel.add_room(room2)
    assert hotel.list_all_rooms() == [sample_room, room2]


def test_hotel_generates_reservation_ids(hotel):
    assert hotel._generate_reservation_id() == "R1"
    assert hotel._generate_reservation_id() == "R2"
    assert hotel._generate_reservation_id() == "R3"


def test_each_hotel_has_its_own_reservation_counter():
    hotel1 = Hotel()
    hotel2 = Hotel()

    assert hotel1._generate_reservation_id() == "R1"
    assert hotel1._generate_reservation_id() == "R2"

    assert hotel2._generate_reservation_id() == "R1"
    assert hotel2._generate_reservation_id() == "R2"

@pytest.fixture
def availability_hotel(sample_guest):
    hotel = Hotel()
    room_101 = Room(
        room_number= 101, room_type=RoomType.SINGLE, nightly_rate=Decimal("100.00")
    )
    hotel._rooms[room_101.room_number] = room_101

    reservation = Reservation(sample_guest, room= room_101, check_in= date(2026, 6, 10),
                               check_out= date(2026, 6, 15),
                               status=ReservationStatus.CONFIRMED,)
    hotel._reservations.append(reservation)
    return hotel

ROOM_101_CASES = [
    pytest.param(date(2026, 6, 5), date(2026, 6, 12), False, id="overlaps_start"),
    pytest.param(date(2026, 6, 13), date(2026, 6, 20), False, id="overlaps_end"),
    pytest.param(date(2026, 6, 11), date(2026, 6, 14), False, id="inside_existing"),
    pytest.param(date(2026, 6, 8), date(2026, 6, 18), False, id="contains_existing"),
    pytest.param(date(2026, 6, 10), date(2026, 6, 15), False, id="identical_dates"),
    pytest.param(date(2026, 6, 5), date(2026, 6, 10), True, id="departs_on_arrival"),
    pytest.param(date(2026, 6, 15), date(2026, 6, 20), True, id="arrives_on_departure"),
    pytest.param(date(2026, 6, 1), date(2026, 6, 5), True, id="completely_before"),
    pytest.param(date(2026, 6, 16), date(2026, 6, 20), True, id="completely_after"),
]

@pytest.mark.parametrize("check_in, check_out, expected", ROOM_101_CASES)
def test_room_101_availability(availability_hotel, check_in, check_out, expected):
    assert availability_hotel.is_room_available(101, check_in, check_out) is expected


def test_different_room_is_available(availability_hotel):
    room_102 = Room(
        room_number=102,
        room_type=RoomType.SINGLE,
        nightly_rate=Decimal("100.00"),
    )
    availability_hotel._rooms[room_102.room_number] = room_102

    assert availability_hotel.is_room_available(
        room_102.room_number, date(2026, 6, 10), date(2026, 6, 15)
    ) is True


def test_cancelled_reservation_does_not_block_room(availability_hotel):
    availability_hotel._reservations[0].status = ReservationStatus.CANCELLED

    assert availability_hotel.is_room_available(
        101, date(2026, 6, 10), date(2026, 6, 15)
    ) is True