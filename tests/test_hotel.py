from decimal import Decimal

import pytest

from rocamonti.exceptions import ConflictError, NotFoundError, RoomNotFoundError
from rocamonti.hotel import Hotel
from rocamonti.models import DocumentType, Guest, Room, RoomType


@pytest.fixture
def hotel():
    """Creates a hotel new and clean hotel instance."""
    return Hotel()
@pytest.fixture
def sample_room():
    return Room(room_number=101, room_type=RoomType.SINGLE, nightly_rate=Decimal("100.00"))
@pytest.fixture
def sample_guest():
    return Guest(name="John Doe", email="john@example.com", phone_number="1234567890",
                 document_type=DocumentType.PASSPORT, document_number="A12345")




def test_add_valid_room(hotel, sample_room):
    hotel.add_room(sample_room)
    assert hotel.get_room(101) == sample_room

def test_add_duplicate_room_raises_error(hotel, sample_room):
    room2 = Room(room_number=101, room_type=RoomType.SINGLE, nightly_rate=Decimal("100.00"))
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
    guest2 = Guest(name="John Doe", email="john@example.com", phone_number="1234567890",
                   document_type=DocumentType.PASSPORT, document_number="A12345")
    with pytest.raises(ConflictError):
        hotel.register_guest(guest2)

def test_get_nonexistent_guest(hotel):
    with pytest.raises(NotFoundError):
        hotel.get_guest("PASSPORT-XYZ")

def test_list_all_guests(hotel, sample_guest):
    hotel.register_guest(sample_guest)
    assert hotel.list_all_guests() == [sample_guest]