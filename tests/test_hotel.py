from datetime import date
from decimal import Decimal

import pytest

from rocamonti.exceptions import (
    ConflictError,
    DataValidationError,
    NotFoundError,
    OverlapError,
    RoomNotFoundError,
)
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
def booked_hotel(sample_guest: Guest, sample_room: Room) -> Hotel:
    hotel = Hotel()
    hotel.add_room(sample_room)
    hotel.register_guest(sample_guest)
    return hotel

@pytest.fixture
def sample_guest():
    return Guest(
        name="John Doe",
        email="john@example.com",
        phone_number="1234567890",
        document_type=DocumentType.PASSPORT,
        document_number="A12345",
    )


def test_add_valid_room(hotel: Hotel, sample_room: Room):
    hotel.add_room(sample_room)
    assert hotel.get_room(101) == sample_room


def test_add_duplicate_room_raises_error(hotel: Hotel, sample_room: Room):
    room2 = Room(
        room_number=101, room_type=RoomType.SINGLE, nightly_rate=Decimal("100.00")
    )
    hotel.add_room(sample_room)
    with pytest.raises(ConflictError):
        hotel.add_room(room2)


def test_get_nonexistent_room(hotel: Hotel):
    with pytest.raises(RoomNotFoundError):
        hotel.get_room(999)


def test_valid_register_guest(hotel: Hotel, sample_guest: Guest):
    hotel.register_guest(sample_guest)
    assert hotel.get_guest("PASSPORT-A12345") == sample_guest


def test_register_duplicate_guest(hotel: Hotel, sample_guest: Guest):
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


def test_get_nonexistent_guest(hotel: Hotel):
    with pytest.raises(NotFoundError):
        hotel.get_guest("PASSPORT-XYZ")


def test_list_all_guests(hotel: Hotel, sample_guest: Guest):
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


def test_list_all_rooms(hotel: Hotel, sample_room: Room):
    room2 = Room(
        room_number=102, room_type=RoomType.SINGLE, nightly_rate=Decimal("100.00")
    )
    hotel.add_room(sample_room)
    hotel.add_room(room2)
    assert hotel.list_all_rooms() == [sample_room, room2]


def test_hotel_generates_reservation_ids(hotel: Hotel):
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
def availability_hotel(booked_hotel: Hotel) -> Hotel:
    booked_hotel.create_reservation(
        guest_id="PASSPORT-A12345",
        room_number=101,
        check_in=date(2026, 6, 10),
        check_out=date(2026, 6, 15),
        today=date(2026, 1, 1),
    )
    return booked_hotel


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
def test_room_101_availability(
    availability_hotel: Hotel, check_in: date, check_out: date, expected: bool
):
    assert availability_hotel.is_room_available(101, check_in, check_out) is expected


def test_different_room_is_available(availability_hotel: Hotel) -> None:
    room_102 = Room(
        room_number=102,
        room_type=RoomType.SINGLE,
        nightly_rate=Decimal("100.00"),
    )
    availability_hotel.add_room(room_102)

    assert (
        availability_hotel.is_room_available(
            room_102.room_number, date(2026, 6, 10), date(2026, 6, 15)
        )
        is True
    )


def test_cancelled_reservation_does_not_block_room(availability_hotel: Hotel) -> None:
    availability_hotel.reservations[0].status = ReservationStatus.CANCELLED

    assert (
        availability_hotel.is_room_available(101, date(2026, 6, 10), date(2026, 6, 15))
        is True
    )


def test_is_room_available_nonexistent_room_raises_error(availability_hotel: Hotel) -> None:
    with pytest.raises(RoomNotFoundError):
        availability_hotel.is_room_available(
            room_number=999,
            check_in=date(2026, 12, 1),
            check_out=date(2026, 12, 5),
        )


@pytest.mark.parametrize(
    ("check_in", "check_out"),
    [
        (date(2026, 12, 5), date(2026, 12, 5)),
        (date(2026, 12, 10), date(2026, 12, 5)),
    ],
)
def test_is_room_available_invalid_date_range(
    availability_hotel: Hotel, check_in: date, check_out: date
) -> None:
    with pytest.raises(DataValidationError):
        availability_hotel.is_room_available(
            room_number=101,
            check_in=check_in,
            check_out=check_out,
        )


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (ReservationStatus.CHECKED_IN, False),
        (ReservationStatus.CHECKED_OUT, False),
        (ReservationStatus.CONFIRMED, False),
        (ReservationStatus.CANCELLED, True),
    ],
)
def test_is_room_available_by_reservation_status(
    availability_hotel: Hotel, status: ReservationStatus, expected: bool
) -> None:
    reservation = availability_hotel.reservations[0]
    reservation.status = status
    
    assert (
        availability_hotel.is_room_available(
            101,
            date(2026, 6, 10),
            date(2026, 6, 15),
        )
        is expected
    )




def test_nonexistent_guest(availability_hotel: Hotel) -> None:
    with pytest.raises(NotFoundError):
        availability_hotel.create_reservation(
            guest_id="nonexistent",
            room_number=101,
            check_in=date(2026, 1, 2),
            check_out=date(2026, 1, 3),
            today=date(2026, 1, 1),
        )

def test_nonexistent_room(availability_hotel: Hotel) -> None:
    with pytest.raises(RoomNotFoundError):
        availability_hotel.create_reservation(
            guest_id="PASSPORT-A12345",
            room_number=999,
            check_in=date(2026, 1, 2),
            check_out=date(2026, 1, 3),
            today=date(2026, 1, 1),
        )

def test_check_in_in_past(availability_hotel: Hotel) -> None:
    with pytest.raises(DataValidationError):
        availability_hotel.create_reservation(
            guest_id="PASSPORT-A12345",
            room_number=101,
            check_in=date(2025, 12, 31),
            check_out=date(2026, 1, 2),
            today=date(2026, 1, 1),
        )
def test_room_overlap(availability_hotel: Hotel) -> None:
    with pytest.raises(OverlapError):
        availability_hotel.create_reservation(
            guest_id="PASSPORT-A12345",
            room_number=101,
            check_in=date(2026, 6, 10),
            check_out=date(2026, 6, 15),
            today=date(2026, 6, 1),
        )
    
def test_create_reservation_success(booked_hotel) -> None:
    reservation = booked_hotel.create_reservation(
        guest_id="PASSPORT-A12345",
        room_number=101,
        check_in=date(2026, 7, 1),
        check_out=date(2026, 7, 5),
        today=date(2026, 6, 30),
    )
    assert reservation.reservation_id == "R1"
    assert reservation.status == ReservationStatus.CONFIRMED
    assert reservation.total_cost == (
        booked_hotel.get_room(101).nightly_rate * 4
    )
    assert (
        booked_hotel.is_room_available(
            101, date(2026, 7, 1), date(2026, 7, 5)
        )
        is False
    )
    assert reservation in booked_hotel.reservations


def test_create_reservation_after_previous_reservation(booked_hotel) -> None:
    first_reservation = booked_hotel.create_reservation(
        guest_id="PASSPORT-A12345",
        room_number=101,
        check_in=date(2026, 7, 6),
        check_out=date(2026, 7, 10),
        today=date(2026, 7, 5),
    )
    assert first_reservation.reservation_id == "R1"

    with pytest.raises(OverlapError) :
        booked_hotel.create_reservation(
            guest_id="PASSPORT-A12345",
            room_number=101,
            check_in=date(2026, 7, 8),
            check_out=date(2026, 7, 12),
            today=date(2026, 7, 5),
         )

    second_reservation = booked_hotel.create_reservation(
        guest_id="PASSPORT-A12345",
        room_number=101,
        check_in=date(2026, 7, 10),
        check_out=date(2026, 7, 15),
        today=date(2026, 7, 5),
        )
    assert second_reservation.reservation_id == "R2"


